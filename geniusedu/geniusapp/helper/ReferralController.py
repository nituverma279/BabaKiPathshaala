from geniusapp import app, db, csrf, config
from flask import current_app, url_for, abort, request, make_response, jsonify, session, json
from geniusapp.model.tables import Referral_program, Wallet, Wallet_trans_log, Referral_setting
from _ast import Param
import datetime

""" Add amount to the wallet using referral program"""


def referral_program(user_id, total_price, message=None):
    try:
        user = Referral_program.query.filter_by(registered_user_id=user_id, is_used=False, is_active=True).first()
        if user:
            
            ref_setting = Referral_setting.query.filter_by(id=1).first()
            discount_amt = ref_setting.amount
            discount_method = ref_setting.dis_type

            if discount_method == 'percent':
                add_wallet_amt = total_price * discount_amt / 100
            elif discount_method == 'amount':
                add_wallet_amt = total_price - discount_amt

            wallet = Wallet.query.filter_by(user_id=user.user_referral_id).first()
            if wallet is None:
                """ Add New Wallet account of the current user """
                db.session.add(Wallet(user.user_referral_id, add_wallet_amt))
                db.session.commit()
                """ Add in wallet trans log"""
                db.session.add(Wallet_trans_log(user.user_referral_id, add_wallet_amt, 'ADD', message))
                db.session.commit()

                """ Update the status of referral program """
                user.is_used = bool(True)
                user.used_date = datetime.datetime.now()
                db.session.commit()
                db.session.close()

            else:
                """ Update Wallet account of the current user """
                wallet.amount = float(wallet.amount) + float(add_wallet_amt)
                db.session.commit()
                """ Add in wallet trans log"""
                db.session.add(Wallet_trans_log(user.user_referral_id, add_wallet_amt, 'ADD', message))
                db.session.commit()

                """ Update the status of referral program """
                user.is_used = bool(True)
                user.used_date = datetime.datetime.now()
                db.session.commit()
                db.session.close()
            return jsonify({'wallet_amount': add_wallet_amt, 'message': 'Wallet amount is updated.'})
        else:
            return jsonify({'wallet_amount': 0, 'message': 'Referral code is already used.'})
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


def wallet_info(user_id):
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({'error': 1, 'amount': 0, 'message': 'Oops! something went wrong.'})
    if wallet:
        amt = float(wallet.amount)
        response = jsonify({'error': 0, 'amount': amt, 'message': 'success'})
    else:
        response = jsonify({'error': 0, 'amount': 0, 'message': 'Your wallet is empty.'})
    return response


def update_wallet(user_id, amount, desc):
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if wallet:
            wallet.amount = float(wallet.amount) - float(amount)
            db.session.commit()
            wt_trans = Wallet_trans_log(user_id=user_id, amount=amount, action='SUBSTRACT', description=desc)
            db.session.add(wt_trans)
            db.session.commit()
            db.session.close()
        else:
            response = jsonify({'error': 1, 'status': 'fail', 'message': 'Wallet account is not valid or not active.'})
            return response
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)
