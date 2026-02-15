# Frontend Setup Guide

## Quick Start

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm start
```

Application will open at: `http://localhost:3000`

## Available Scripts

### `npm start`
Runs the app in development mode.

### `npm build`
Builds the app for production to the `build` folder.

### `npm test`
Launches the test runner.

## Configuration

### Backend API URL
The app uses a proxy configuration in `package.json`:
```json
"proxy": "http://localhost:5000"
```

If your backend runs on a different port, update this value.

### For Production
Create a `.env.production` file:
```env
REACT_APP_API_URL=https://your-api-domain.com
```

Update API calls to use:
```javascript
const API_URL = process.env.REACT_APP_API_URL || '';
fetch(`${API_URL}/api/search-hospitals-osm`, {...})
```

## Customization

### Change Colors
Edit CSS variables in `src/index.css`:
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
}
```

### Add New Features
Components are located in `src/components/`:
- `SearchForm.js` - Search input form
- `HospitalsList.js` - List of hospitals
- `MapView.js` - Interactive map
- `Favorites.js` - Saved hospitals
- `SearchHistory.js` - Recent searches

## Building for Production

```bash
# Create optimized build
npm run build

# Test production build locally
npm install -g serve
serve -s build
```

## Deployment

### Vercel
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod
```

### GitHub Pages
```bash
npm install --save-dev gh-pages

# Add to package.json
"homepage": "https://yourusername.github.io/nearby-care",
"scripts": {
  "predeploy": "npm run build",
  "deploy": "gh-pages -d build"
}

npm run deploy
```

## Troubleshooting

### Map Not Displaying
Check that Leaflet CSS is loaded in `public/index.html`:
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

### API Connection Issues
1. Make sure backend is running on port 5000
2. Check proxy configuration in `package.json`
3. Verify CORS is enabled on backend

### Dependencies Installation Fails
Try:
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```
