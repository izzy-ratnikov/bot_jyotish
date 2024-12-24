from src.commands.start import router as get_user_data
from src.dispatcher.dispatcher import dp
from src.handlers.form_handlers import router as form_router

dp.include_router(get_user_data)
dp.include_router(form_router)

