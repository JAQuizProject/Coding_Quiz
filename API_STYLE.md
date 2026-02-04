# Backend API Style Guide

이 문서는 백엔드 서버 프로젝트에서 API 설계와 네이밍(라우터/서비스/레포지토리) 컨벤션을 정의합니다.

**Base URL**

- `https://router.tvcf.co.kr/api/{project-name}/{version}/{api-name}/`
- 예: `https://router.tvcf.co.kr/api/admin/v1/keywords/`

**1. Interface Layer (Router)**

- URL 구조
  - `/api/v1/{resources}`                      # 리소스 컬렉션
  - `/api/v1/{resources}/{id}`                 # 단일 리소스
  - `/api/v1/{resources}/{id}/{sub-resources}` # 하위 리소스
  - `/api/v1/{resources}/{id}/{action}`        # 특수 동작

- Router 함수명 (FastAPI 예시)
  - `@router.get("/{id}")`
    - `async def get_{resource}_detail(...)`     # GET /api/v1/users/1

  - `@router.get("/")`
    - `async def list_{resources}(...)`          # GET /api/v1/users

  - `@router.post("/")`
    - `async def create_{resource}(...)`         # POST /api/v1/users

  - `@router.put("/{id}")`
    - `async def update_{resource}(...)`         # PUT /api/v1/users/1

  - `@router.delete("/{id}")`
    - `async def delete_{resource}(...)`         # DELETE /api/v1/users/1

  - 하위 리소스
    - `@router.get("/{parent_id}/{sub_resources}")`
      - `async def list_{parent}_{sub_resources}(...)` # GET /api/v1/users/1/orders

  - 특수 동작
    - `@router.post("/{id}/{action}")`
      - `async def {action}_{resource}(...)`       # POST /api/v1/orders/1/cancel

**2. Service Layer**

- Service 함수명

  ```py
  class ResourceService:
      # 조회
      async def find_{resource}(self, id: int):
          ...
      async def find_all_{resources}(self, filters: dict):
          ...
      async def find_{resources}_by_{field}(self, value: Any):
          ...

      # 생성/수정/삭제
      async def register_{resource}(self, data: dict):
          ...
      async def modify_{resource}(self, id: int, data: dict):
          ...
      async def remove_{resource}(self, id: int):
          ...

      # 비즈니스 로직
      async def process_{action}(self, id: int, data: dict):
          ...
      async def validate_{condition}(self, data: dict):
          ...
      async def analyze_{data}(self, id: int):
          ...
  ```

**3. Repository Layer**

- Repository 함수명

  ```py
  class ResourceRepository:
      # 조회
      async def select_{resource}(self, id: int):
          ...
      async def select_all_{resources}(self, filters: dict):
          ...
      async def select_{resources}_by_{field}(self, value: Any):
          ...

      # 생성/수정/삭제
      async def insert_{resource}(self, data: dict):
          ...
      async def update_{resource}(self, id: int, data: dict):
          ...
      async def delete_{resource}(self, id: int):
          ...
  ```

**4. 실제 적용 예시 (주문 시스템)**

- Router

  ```py
  @router.get("/orders/{order_id}")
  async def get_order_detail(order_id: int):
      return await order_service.find_order(order_id)
  ```

- Service

  ```py
  class OrderService:
      async def find_order(self, order_id: int):
          return await self.order_repo.select_order(order_id)

      async def process_payment(self, order_id: int, payment_data: dict):
          order = await self.find_order(order_id)
          await self.validate_payment(payment_data)
          return await self.modify_order_status(order_id, "PAID")
  ```

- Repository

  ```py
  class OrderRepository:
      async def select_order(self, order_id: int):
          return await self.db.orders.find_one({"id": order_id})

      async def update_order_status(self, order_id: int, status: str):
          return await self.db.orders.update_one(
              {"id": order_id},
              {"$set": {"status": status}}
          )
  ```

---

원하시면 이 규칙에 맞춰 기존 라우터 파일(`app/routes/quiz.py`)을 리팩토링하거나, 다른 API 엔드포인트들을 표준화해 드리겠습니다. 어떤 파일을 자동으로 변환할지 알려주세요.
