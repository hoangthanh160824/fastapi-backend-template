# Smoke Test Documentation

## Cách hoạt động của hệ thống khi chạy

### 1. Quy trình khởi động (Startup Flow)

Khi chạy `docker compose up`, hệ thống thực hiện các bước sau:

#### a. Database Service (PostgreSQL)
- Khởi động PostgreSQL container
- Health check: kiểm tra database ready với `pg_isready`
- Retry 5 lần, mỗi 10 giây
- Start period: 30 giây

#### b. Prestart Service (Initialization)
- **Chờ database healthy** trước khi chạy
- Thực thi `scripts/prestart.sh`:
  1. **backend_pre_start.py**: 
     - Kiểm tra kết nối database
     - Retry tối đa 5 phút (60*5 attempts)
     - Wait 1 giây giữa các lần thử
  2. **Alembic migrations**: 
     - Chạy `alembic upgrade head`
     - Apply tất cả database migrations
  3. **initial_data.py**:
     - Tạo superuser đầu tiên
     - Khởi tạo dữ liệu mẫu

#### c. Backend Service (FastAPI)
- **Chờ 2 điều kiện**:
  - Database service healthy
  - Prestart service completed successfully
- Khởi động FastAPI application
- Expose port 8000

#### d. Adminer Service
- Database management UI
- Phụ thuộc vào database service
- Accessible at port 8080

### 2. Test Scenarios

#### Manual Smoke Test
```bash
# Build và start services
docker compose build
docker compose up -d --wait backend adminer

# Test health check
curl http://localhost:8000/api/v1/utils/health-check/

# Test database connectivity
curl http://localhost:8000/api/v1/utils/db-check/

# Test API docs
curl http://localhost:8000/docs

# Clean up
docker compose down -v --remove-orphans
```

#### Automated Smoke Test (GitHub Actions)
- **Trigger**: Push to branch `break` or Pull Request
- **File**: `.github/workflows/test-docker-compose.yml`
- **Steps**:
  1. Build Docker images
  2. Start services với --wait flag
  3. Test health check endpoint
  4. Test database connectivity
  5. Clean up resources

#### Backend Unit Tests
```bash
cd backend
uv run bash scripts/tests-start.sh
```

**Test flow**:
1. **tests_pre_start.py**: Kiểm tra database connection
2. **pytest**: Chạy toàn bộ test suite
3. **coverage**: Generate coverage report

### 3. Dependency Chain

```
PostgreSQL (healthy)
    ↓
Prestart (migrations + initial data)
    ↓
Backend (FastAPI app)
    ↓
Ready for requests
```

### 4. Error Handling

- **Database không available**: 
  - Prestart retry 5 phút
  - Backend không start nếu prestart fail
  
- **Migration fail**: 
  - Prestart service exit với error
  - Backend không start
  
- **Health check fail**:
  - Service được mark là unhealthy
  - Docker compose có thể restart service

### 5. Environment Variables Required

Critical variables từ `.env`:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `SECRET_KEY`
- `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`
- `DOMAIN`, `ENVIRONMENT`
- `DOCKER_IMAGE_BACKEND`

### 6. Complete Test Suite

```bash
# Full smoke test với verification
docker compose build
docker compose up -d --wait backend adminer

# Verify all endpoints
curl -f http://localhost:8000/api/v1/utils/health-check/ && echo "✅ Health check passed!"
curl -f http://localhost:8000/api/v1/utils/db-check/ && echo "✅ Database connected!"
curl -f http://localhost:8000/docs && echo "✅ API docs available!"

# Check logs nếu cần
docker compose logs backend
docker compose logs prestart

# Clean up
docker compose down -v --remove-orphans
```

Tất cả các smoke test đều hoạt động bình thường với backend API-only template! 🎉