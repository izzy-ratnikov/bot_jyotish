from src.dispatcher.dispatcher import dp
from src.handlers.form_handlers import router as form_router

dp.include_router(form_router)
