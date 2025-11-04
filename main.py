from api.api import shyeri_meme_app
import uvicorn
from core.core import conf
PORT = conf.get()["api"]["port"]

if __name__ == '__main__':
    uvicorn.run(shyeri_meme_app, host='0.0.0.0', port=PORT)