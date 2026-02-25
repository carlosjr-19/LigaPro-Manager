from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import User
import stripe
import os

premium_bp = Blueprint('premium', __name__)

@premium_bp.route('/premium')
@login_required
def premium():
    return render_template('premium.html')


@premium_bp.route('/premium/captain')
@login_required
def captain_premium():
    return render_template('captain_premium.html')


@premium_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        plan_type = request.args.get('plan', 'owner') # 'owner' (subscription) or 'captain' (one-time)
        
        if plan_type == 'captain':
             price_id = current_app.config['STRIPE_CAPTAIN_PRICE_ID']
             mode = 'payment'
        elif plan_type == 'annual':
             price_id = current_app.config['STRIPE_PRICE_ANUAL_ID']
             mode = 'payment'
        elif plan_type == 'ultra_monthly':
             price_id = current_app.config['STRIPE_ULTRA_PRICE_MENSUAL']
             mode = 'subscription'
        elif plan_type == 'ultra_annual':
             price_id = current_app.config['STRIPE_ULTRA_PRICE_ANUAL']
             mode = 'subscription'
        else:
             price_id = current_app.config['STRIPE_PRICE_ID']
             mode = 'subscription'

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode=mode,
            metadata={'plan_type': plan_type},
            success_url=url_for('premium.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('premium.premium', _external=True) if plan_type != 'captain' else url_for('premium.captain_premium', _external=True),
            customer_email=current_user.email,
            client_reference_id=current_user.id,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error al conectar con Stripe: {str(e)}', 'danger')
        return redirect(url_for('premium.premium'))


@premium_bp.route('/success')
@login_required
def success():
    session_id = request.args.get('session_id')
    if session_id:
        try:
            # Recuperar la sesión de Stripe para verificar qué se compró
            session = stripe.checkout.Session.retrieve(session_id)
            plan_type = session.get('metadata', {}).get('plan_type')
            
            if plan_type and 'ultra' in plan_type:
                current_user.is_ultra = True
                flash('¡Gracias por tu suscripción! Tu cuenta ahora es Ultra Premium.', 'success')
                print(f"🚀 SUCCESS: Ultra activado por sesión para {current_user.email}")
            else:
                current_user.is_premium = True
                flash('¡Gracias por tu suscripción! Tu cuenta ahora es Premium.', 'success')
                print(f"✅ SUCCESS: Premium activado por sesión para {current_user.email}")
                
            db.session.commit()
        except Exception as e:
            print(f"❌ SUCCESS ERROR: No se pudo verificar la sesión: {e}")
            # Fallback seguro
            current_user.is_premium = True
            db.session.commit()
            flash('Tu suscripción ha sido procesada.', 'success')
    else:
        # Si no hay session_id, al menos activamos premium (comportamiento anterior)
        current_user.is_premium = True
        db.session.commit()
        flash('Suscripción activada.', 'success')
        
    return redirect(url_for('main.dashboard'))

@premium_bp.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not webhook_secret:
        return 'Webhook secret not configured', 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Payload inválido
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida (alguien intenta hackear)
        return 'Invalid signature', 400

    # Manejar el evento: Pago Exitoso
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Recuperamos el ID del usuario que guardamos al crear la sesión
        user_id = session.get('client_reference_id')
        
        if user_id:
            # Buscamos al usuario y activamos el Premium de verdad
            # Usamos un contexto de aplicación por si acaso (aunque Flask suele manejarlo)
            try:
                user = User.query.get(user_id)
                if user:
                    user.is_premium = True
                    
                    # Check for Ultra plan in metadata
                    plan_type = session.get('metadata', {}).get('plan_type')
                    if plan_type and 'ultra' in plan_type:
                        user.is_ultra = True
                        print(f"💎 WEBHOOK: Ultra activado para el usuario {user.email}")
                    
                    db.session.commit()
                    print(f"✅ WEBHOOK: Premium activado para el usuario {user.email}")
                else:
                    print(f"⚠️ WEBHOOK: Usuario {user_id} no encontrado.")
            except Exception as e:
                print(f"❌ WEBHOOK ERROR: No se pudo actualizar la DB: {e}")
                db.session.rollback()

    return jsonify(success=True)
