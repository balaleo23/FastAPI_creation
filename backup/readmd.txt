Step 3: Set Up a Virtual Environment
Open VS Code.
Open Terminal: You can do this by going to View > Terminal or by pressing `Ctrl + ``.
Navigate to Your Project Directory: Use the terminal to navigate to the directory where you want to create your FastAPI project.
Create a Virtual Environment: Run the following command to create a virtual environment:
bash
Copy code
python -m venv env
Activate the Virtual Environment:
On Windows:
bash
Copy code
.\env\Scripts\activate
On macOS and Linux:
bash
Copy code
source env/bin/activate
Step 4: Install FastAPI and Uvicorn
Install FastAPI: Run the following command in the terminal:
bash
Copy code
pip install fastapi
Install Uvicorn: Uvicorn is an ASGI server used to run FastAPI applications. Install it using:
bash
Copy code
pip install uvicorn
Step 5: Create a FastAPI Application
Create a New Python File: In your project directory, create a new file named main.py.

uvicorn main:app --reload
