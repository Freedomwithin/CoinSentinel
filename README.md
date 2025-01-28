# CoinSentinel

An advanced cryptocurrency tracking and analysis application built with Python.

## Features

- Real-time market overview
- Portfolio management
- Price prediction using machine learning
- Sentiment analysis
- Custom price alerts
- Cryptocurrency news aggregation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Freedomwithin/CoinSentinel/.git
   cd CoinSentinel
   
2. Create and activate a virtual environment:

   ```bash
    python3 -m venv venv
    source venv/bin/activate
3. Upgrade pip (optional but recommended):

   ```bash
    pip install --upgrade pip
4. Install required packages:

   ```bash
    pip install --upgrade -r requirements.txt

## Usage

Run the application

   ```bash
python main_app_pyqt.py
   ```

## Additional Options

You can create an executable `.sh` or `.command` file to simplify running the project:

1. Create an executable file using a text editor:
   ```bash
   nano run.sh  
2. Add the following content to the file:
   ```bash
   cd CoinSentinel
   source venv/bin/activate
   pip install --update pip 
   pip install -r requirements.txt
   python main_app_pyqt.py
   ```
 Save and exit the editor (Ctrl+O, Enter, then Ctrl+X in nano).

4. Make the script executable:
   ```bash
   chmod +x main_app_pyqt.py
   ```
5. Run the script:
    ```bash
    ./run.sh
    ```

For macOS users creating a .command file, follow the same steps but name the file run.command. The execution process remains the same.

## Dependencies

See `requirements.txt` for a full list of dependencies.

## Contributing

Contributions, issues, and feature requests are welcome!

 ## License
This project is licensed under the MIT License - see the LICENSE.md file for details.


