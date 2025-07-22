# 🔧 CORS Troubleshooting Guide for AWS Lambda

## 🎯 What is CORS and Why It Matters

CORS (Cross-Origin Resource Sharing) is a security feature that controls which domains can access your API from web browsers. Without proper CORS configuration, your frontend will get "blocked by CORS policy" errors.

---

## ✅ Our Enhanced CORS Configuration

### 1. **API Gateway Level CORS**
- Configured in `serverless.yml` for automatic OPTIONS handling
- Headers whitelisted for all standard operations
- Supports preflight requests

### 2. **Lambda Function Level CORS**
- Custom CORS handler ensures headers on ALL responses
- Handles error responses with proper CORS headers
- Manages preflight OPTIONS requests

### 3. **FastAPI Application Level CORS**
- CORSMiddleware configured in `app/main.py`
- Triple-layer protection for maximum compatibility

---

## 🚨 Common CORS Errors & Solutions

### Error 1: "Access to fetch at 'API_URL' from origin 'FRONTEND_URL' has been blocked by CORS policy"

**Cause**: Missing Access-Control-Allow-Origin header

**Solution**: Our configuration includes:
```yaml
cors:
  origin: '*'  # Allows all origins
```

**To restrict to specific domains**:
```yaml
cors:
  origin: 'https://yourdomain.com'
```

### Error 2: "Request header 'content-type' is not allowed by Access-Control-Allow-Headers"

**Cause**: Missing required headers in CORS configuration

**Solution**: We include all standard headers:
```yaml
headers:
  - Content-Type
  - Authorization
  - X-Api-Key
  - X-Requested-With
```

### Error 3: "Method 'POST' is not allowed by Access-Control-Allow-Methods"

**Cause**: Missing HTTP methods in CORS config

**Solution**: We allow all methods:
```yaml
Access-Control-Allow-Methods: "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT"
```

### Error 4: "CORS error on error responses (4xx/5xx)"

**Cause**: Error responses don't include CORS headers

**Solution**: Our `CORSHandler` ensures ALL responses have CORS headers:
```python
# Even error responses get CORS headers
return CORSHandler.handle_error(error, status_code=500)
```

---

## 🧪 Testing CORS Configuration

### Test 1: Preflight Request (OPTIONS)
```bash
curl -X OPTIONS https://your-api-url.amazonaws.com/prod/api/health \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

**Expected Response**:
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT
< Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization...
```

### Test 2: Actual API Request
```bash
curl -X POST https://your-api-url.amazonaws.com/prod/api/analyze \
  -H "Content-Type: application/json" \
  -H "Origin: https://yourdomain.com" \
  -d '{"cv_text":"test","job_description":"test"}' \
  -v
```

**Expected Response**:
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: *
< Content-Type: application/json
```

### Test 3: Error Response CORS
```bash
curl -X POST https://your-api-url.amazonaws.com/prod/api/nonexistent \
  -H "Origin: https://yourdomain.com" \
  -v
```

**Expected**: Even 404 errors should have CORS headers.

---

## 🌐 Frontend Integration Examples

### JavaScript Fetch
```javascript
// This should work without CORS errors
fetch('https://your-api-url.amazonaws.com/prod/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    cv_text: "John Smith, Software Engineer",
    job_description: "Python Developer"
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### React/Axios Example
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://your-api-url.amazonaws.com/prod',
  headers: {
    'Content-Type': 'application/json',
  }
});

// This should work without CORS issues
const analyzeCV = async (cvText, jobDescription) => {
  try {
    const response = await apiClient.post('/api/analyze', {
      cv_text: cvText,
      job_description: jobDescription
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
  }
};
```

---

## 🔧 Advanced CORS Configuration

### Production Security (Restrict Origins)
Edit `serverless.yml`:
```yaml
cors:
  origin: 'https://yourdomain.com'  # Only allow your domain
  credentials: true  # If you need cookies/auth
```

### Multiple Allowed Origins
```yaml
# Use environment variable for dynamic origins
environment:
  CORS_ORIGINS: '["https://yourdomain.com","https://staging.yourdomain.com"]'
```

### Custom Headers
```yaml
cors:
  headers:
    - Content-Type
    - Authorization
    - X-Custom-Header  # Add your custom headers
```

---

## 🐛 Debugging CORS Issues

### 1. **Check Browser Developer Tools**
- Open Network tab
- Look for OPTIONS preflight requests
- Check response headers in failed requests

### 2. **Common Browser Error Messages**
```
❌ "has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header"
✅ Solution: Check API Gateway CORS configuration

❌ "has been blocked by CORS policy: Method not allowed"
✅ Solution: Add the HTTP method to allowedMethods

❌ "has been blocked by CORS policy: Request header not allowed"
✅ Solution: Add the header to allowedHeaders
```

### 3. **Test with CURL First**
Before testing in browser, verify CORS headers with curl:
```bash
# Check if CORS headers are present
curl -I https://your-api-url.amazonaws.com/prod/health
```

### 4. **CloudWatch Logs**
```bash
# Check Lambda logs for CORS-related errors
serverless logs -f api -t
```

---

## ⚡ Quick Fixes

### Fix 1: Redeploy with CORS Changes
```bash
serverless deploy
```

### Fix 2: Test CORS Headers
```bash
# Quick CORS test script
curl -X OPTIONS https://your-api-url.amazonaws.com/prod/api/health -v | grep -i "access-control"
```

### Fix 3: Verify API Gateway Configuration
1. Go to AWS Console → API Gateway
2. Find your API → Resources
3. Click on any method → Actions → Enable CORS
4. Verify settings match our configuration

---

## 📊 CORS Configuration Checklist

- [ ] ✅ **serverless.yml** has detailed CORS configuration
- [ ] ✅ **lambda_handler.py** includes CORSHandler
- [ ] ✅ **app/main.py** has CORSMiddleware
- [ ] ✅ **API Gateway** responses include CORS headers
- [ ] ✅ **OPTIONS** preflight requests work
- [ ] ✅ **Error responses** include CORS headers
- [ ] ✅ **Frontend** can make requests without CORS errors

---

## 🎯 Final Verification

After deployment, this JavaScript should work in your browser console:
```javascript
fetch('https://your-api-url.amazonaws.com/prod/health')
  .then(r => r.json())
  .then(data => console.log('✅ CORS working:', data))
  .catch(err => console.error('❌ CORS error:', err));
```

---

**🚀 With our triple-layer CORS protection, your API will work seamlessly with any frontend framework!**