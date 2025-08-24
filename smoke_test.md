  Bạn có thể chạy smoke test theo các cách sau:

  1. Manual smoke test (như vừa thực hiện):

  # Build và start services
  docker compose build
  docker compose up -d --wait backend adminer

  # Test health check
  curl http://localhost:8000/api/v1/utils/health-check/

  # Test API docs
  curl http://localhost:8000/docs

  # Clean up
  docker compose down -v --remove-orphans

  2. Automated smoke test (GitHub Actions):

  - Workflow tự động chạy khi push code
  - Kiểm tra trong .github/workflows/test-docker-compose.yml
  - Chạy các test tương tự ở trên

  3. Backend unit tests:

  cd backend
  uv run bash scripts/tests-start.sh

  4. Chạy complete smoke test suite:

  # Chạy workflow giống GitHub Actions
  docker compose build
  docker compose up -d --wait backend adminer
  curl -f http://localhost:8000/api/v1/utils/health-check/ && echo "✅ Smoke test passed!"
  docker compose down -v --remove-orphans

  Tất cả các smoke test đều hoạt động bình thường với backend API-only template! 🎉