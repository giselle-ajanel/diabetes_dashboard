Must first create virtual environment to run application on local machine: 
-- on mac
python -3 venv venv 
source venv/bin/activate
pip install -r downloads/DSCI551/requirements.txt
cd downloads
cd DSCI551
ls (to confirm the folders in our project code)
streamlit run app.py 

-- on windows 

```powershell
python -3 -m venv venv
```

```powershell
venv\Scripts\activate
```

```powershell
pip install -r downloads/DSCI551/requirements.txt
```

```powershell
cd downloads
cd DSCI551
```

```powershell
streamlit run app.py
```
