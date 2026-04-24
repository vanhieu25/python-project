# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A desktop car dealership management system built with Python and PyQt6. Uses a layered architecture with Repository pattern for data access.

**Default login**: admin / admin123

## Common Commands

### Run Application
```bash
# Activate virtual environment first (Windows)
venv\Scripts\activate

# Run the application
python src/main.py
```

### Run Tests
```bash
# All unit tests
python -m unittest discover tests/ -v

# Single test file
python -m unittest tests.test_car_service -v

# Single test class
python -m unittest tests.test_car_service.TestCarService -v

# Single test method
python -m unittest tests.test_car_service.TestCarService.test_create_car -v
```

### Run UI Tests
```bash
# All UI tests
python run_ui_tests.py

# Individual UI test
python run_ui_tests.py --test login
python run_ui_tests.py --test employee_list
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/

# Type check
mypy src/
```

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│  Presentation Layer (PyQt6)         │
│  - views/dialogs/*.py               │
│  - views/widgets/*.py               │
│  - ui/*/                            │
├─────────────────────────────────────┤
│  Business Logic Layer (Services)    │
│  - services/*_service.py            │
├─────────────────────────────────────┤
│  Data Access Layer (Repositories)   │
│  - repositories/*_repository.py     │
├─────────────────────────────────────┤
│  Database Layer (SQLite)            │
│  - database/db_helper.py            │
│  - database/schema.sql              │
└─────────────────────────────────────┘
```

### Data Flow

1. **UI** creates/updates → calls **Service** method
2. **Service** validates → calls **Repository** method
3. **Repository** executes SQL via **DatabaseHelper**
4. **Repository** returns dict/data → **Service** converts to **Model**
5. **Service** returns **Model** → **UI** displays

### Key Patterns

**Repository Pattern**: Each entity has a repository class (e.g., `CarRepository`, `UserRepository`) that handles all database operations for that entity.

**Service Layer**: Contains business logic, validation, and orchestrates repositories. Services raise custom exceptions (e.g., `CarServiceError`, `DuplicateVINError`).

**Models**: Data classes with `from_dict()` and `to_dict()` methods for database conversion.

**Validators**: Separate validator classes (e.g., `CarValidator`) for input validation that raise validation errors with field information.

## Code Conventions

### Naming
- Variables/functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Private methods: `_prefix`

### Error Handling
```python
# Services define custom exceptions
class CarServiceError(Exception):
    pass

# Services catch repo exceptions and re-raise as domain exceptions
try:
    self.car_repo.create(car_data)
except sqlite3.IntegrityError as e:
    raise DuplicateVINError(f"VIN '{vin}' đã tồn tại")
```

### Database Helper
Always use the context manager pattern via `DatabaseHelper`:
```python
db = DatabaseHelper("data/car_management.db")
results = db.fetch_all("SELECT * FROM cars WHERE status = ?", (status,))
```

## Git Workflow

**Current branch**: `feature/0-foundation-auth`

**Main branch**: `main`

**Feature branches**: 15 branches following pattern `feature/{n}-{name}`
- Feature 0 (Foundation) must complete before other features
- Core features (1, 2, 3) can develop in parallel after Feature 0

**Commit convention**: `type: description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Script helper**: `./git-workflow.sh` for branch management
```bash
./git-workflow.sh list      # List all feature branches
./git-workflow.sh switch feature/1-car-management
```

## Project Structure Notes

- `src/views/`: PyQt6 dialogs and widgets using Apple-inspired design
- `src/ui/`: Alternative UI components (newer car-related UI)
- `src/validators/`: Input validation logic separate from services
- `data/`: SQLite database (gitignored)
- `sprints/`: Sprint documentation organized by feature
- `designs/DESIGN.md`: Apple-inspired design system with color palette and typography

## Design System

Apple-inspired minimalist design defined in `designs/DESIGN.md`:
- **Primary blue**: `#0071e3` (buttons, links, focus states)
- **Background light**: `#f5f5f7`
- **Background dark**: `#000000`
- **Text light bg**: `#1d1d1f`
- **Border radius**: 8px for buttons, 5-8px for cards
- **Shadow**: `rgba(0, 0, 0, 0.22) 3px 5px 30px 0px`

## Testing Conventions

- Tests use temporary databases created in setUp/torn down in tearDown
- Test files named `test_*.py`
- Test classes extend `unittest.TestCase`
- UI tests require desktop environment (cannot run headless)

## Important Files

- `src/database/schema.sql`: Database schema with seed data
- `src/database/db_helper.py`: Database connection helper with context managers
- `requirements.txt`: All dependencies including PyQt6, bcrypt, reportlab
