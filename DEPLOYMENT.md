# Deployment Information

## Public URL
https://d12-agent-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://d12-agent-production.up.railway.app/health
# Expected: {"status": "ok", "version": "...", ...}
```

### API Test (with authentication)
```bash
curl -X POST https://d12-agent-production.up.railway.app/ask \
  -H "X-API-Key: production-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello Agent!"}'
```

## Environment Variables Set
- `PORT` = `8000`
- `REDIS_URL` = `redis://default:xxxxxx@containers-us-west-xx.railway.app:6379`
- `AGENT_API_KEY` = `production-secret-key-123`
- `LOG_LEVEL` = `INFO`
- `DEBUG` = `False`
- `ENVIRONMENT` = `production`
- `RATE_LIMIT_PER_MINUTE` = `10`
- `DAILY_BUDGET_USD` = `10.0`

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
