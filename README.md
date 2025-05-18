**Running the Backend**

1.  **Create a Virtual Environment (Recommended):**

    * **Linux:**

        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

    * **Windows:**

        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

2.  **Install Dependencies:**

    * **Linux/Windows:**

        ```bash
        pip install -r requirements.txt
        ```


3.  **Start the Application:**

    * **Linux/Windows:**

        ```bash
        uvicorn main:app --reload
        ```

4.  **View the API Documentation:**



      **Once the application is running, you can view the automatically generated API documentation at:**

        http://localhost:8000/docs



* **Additional info:**

  We are using the SQLite database, so no additional setup is required, the database will be automatically generated at a specified location. If you want to specify a different location, modify the `SQLALCHEMY_DATABASE_URL` in `database.py`:
