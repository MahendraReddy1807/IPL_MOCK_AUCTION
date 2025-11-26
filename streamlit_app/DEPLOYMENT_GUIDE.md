# Deployment Guide

## Testing Locally

Before deploying, test the application locally:

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

Open multiple browser windows/tabs to test multi-user functionality.

## Deploy to Streamlit Cloud

1. **Prepare Repository:**
   - Ensure all code is committed to Git
   - Push to GitHub

2. **Deploy:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app/app.py`
   - Click "Deploy"

3. **Configuration:**
   - No additional configuration needed for basic deployment
   - Database will be created automatically on first run
   - **Note**: Database is stored in `/tmp` on Streamlit Cloud and is ephemeral (resets on app restart)
   - For persistent data, consider using a cloud database (PostgreSQL, etc.)

4. **Access:**
   - Your app will be available at: `https://[your-app-name].streamlit.app`

## Testing Checklist

Before marking deployment complete, verify:

- [ ] App loads without errors
- [ ] Can create a room
- [ ] Can join a room with code
- [ ] Can configure team
- [ ] Can start auction (as host)
- [ ] Can place bids
- [ ] Timer counts down correctly
- [ ] Players are assigned correctly
- [ ] Results page shows ratings
- [ ] Multiple users can interact simultaneously

## Next Steps

After deployment:

1. **Run Unit Tests** (Task 16)
2. **Run Property-Based Tests** (Task 17)
3. **Run Integration Tests** (Task 18)

See test files in `tests/` directory for implementation.
