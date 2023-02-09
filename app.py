from app import app, db, login_manager
from app.routes import User, Task

if __name__ == '__main__':
	app.run(debug = True)