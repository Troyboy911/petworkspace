"""
Celery tasks for dropshipping operations
"""

from celery import shared_task
from src.dropshipping.dropshipping_manager import DropshippingManager
from config.config import Config
from src.models import create_database, create_session, Order

@shared_task(name='tasks.process_orders')
def process_orders(order_id=None):
    """
    Task to process and fulfill orders
    
    Args:
        order_id: Optional specific order ID to process
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        dropshipping_manager = DropshippingManager(config)
        
        # Get pending orders
        if order_id:
            pending_orders = session.query(Order).filter_by(
                id=order_id,
                status='pending'
            ).all()
        else:
            pending_orders = session.query(Order).filter_by(
                status='pending'
            ).limit(10).all()
        
        if not pending_orders:
            return {
                'status': 'warning',
                'message': 'No pending orders to process'
            }
        
        processed_orders = []
        
        # Process each order
        for order in pending_orders:
            try:
                success = dropshipping_manager.auto_fulfill_order(order)
                
                if success:
                    processed_orders.append({
                        'order_id': order.order_id,
                        'status': order.status,
                        'tracking_number': order.tracking_number
                    })
            
            except Exception as e:
                continue
        
        session.commit()
        
        return {
            'status': 'success',
            'processed_count': len(processed_orders),
            'orders': processed_orders
        }
        
    except Exception as e:
        session.rollback()
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()

@shared_task(name='tasks.update_inventory')
def update_inventory():
    """
    Task to update inventory levels and pricing
    """
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    
    try:
        dropshipping_manager = DropshippingManager(config)
        
        # Monitor inventory levels
        inventory_alerts = dropshipping_manager.monitor_inventory_levels(session)
        
        # Update pricing
        pricing_updates = dropshipping_manager.dynamic_pricing_adjustment(session)
        
        return {
            'status': 'success',
            'inventory_alerts': len(inventory_alerts),
            'pricing_updates': len(pricing_updates)
        }
        
    except Exception as e:
        session.rollback()
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        session.close()