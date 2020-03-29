# import logging
from app import create_app


app = create_app()

# logging.basicConfig(filename='request.log', level=logging.CRITICAL)

if __name__ == "__main__":
    app.run(debug=True)