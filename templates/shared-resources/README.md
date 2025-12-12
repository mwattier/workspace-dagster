# Shared Dagster Resources

**Purpose**: Reusable Dagster resources that can be used across multiple modules.

**Location**: `~/workspace/patterns/dagster/shared-resources/`

---

## Available Resources

### Metabase Resource (`metabase_resource.py`)

Provides centralized access to Metabase API for querying saved cards/questions.

**Features**:
- Query Metabase cards and get results in JSON, CSV, or DataFrame format
- Get card metadata
- Comprehensive error handling with clear failure messages
- Centralized API key management

**Environment Variables**:
```bash
METABASE_URL=https://metabase.example.com
METABASE_API_KEY=mb_xxx...
```

**Usage in Your Module**:

```python
# In your assets.py
import os
from dagster import asset, AssetExecutionContext
import sys
from pathlib import Path
sys.path.append(str(Path.home() / 'workspace'))
from patterns.dagster.shared_resources.metabase_resource import metabase_resource

@asset(required_resource_keys={"metabase"})
def my_data_from_metabase(context: AssetExecutionContext):
    """Extract data from Metabase card."""
    metabase = context.resources.metabase
    card_id = int(os.environ["MY_MODULE_METABASE_CARD_ID"])

    # Get data as JSON (list of dicts)
    data = metabase.query_card(card_id, format='json')

    # Or as DataFrame for processing
    df = metabase.query_card(card_id, format='dataframe')

    return {"records": len(data)}
```

```python
# In your __init__.py
from dagster import Definitions
from .assets import my_data_from_metabase
import sys
from pathlib import Path
sys.path.append(str(Path.home() / 'workspace'))
from patterns.dagster.shared_resources.metabase_resource import metabase_resource

defs = Definitions(
    assets=[my_data_from_metabase],
    resources={
        "metabase": metabase_resource,
    }
)
```

**Card ID Configuration**:

Each module should define its own card IDs in environment variables with a module-specific prefix:

```bash
# In your module's .env
# Example: customer-analytics module
CUSTOMER_ANALYTICS_ORDERS_CARD_ID=123

# Example: sales-pipeline module
SALES_PIPELINE_DEALS_CARD_ID=456
SALES_PIPELINE_REVENUE_CARD_ID=789
```

This allows multiple modules to share the same Metabase credentials while querying different cards.

---

## Benefits

### Centralized Credential Management

**Before** (credentials per module):
```bash
# customer-analytics/.env
METABASE_URL=https://metabase.example.com
METABASE_API_KEY=mb_xxx...

# sales-pipeline/.env
METABASE_URL=https://metabase.example.com
METABASE_API_KEY=mb_xxx...
```
❌ Duplicated credentials
❌ Update in multiple places if credentials change
❌ Higher security risk

**After** (shared resource):
```bash
# workspace .env (shared)
METABASE_URL=https://metabase.example.com
METABASE_API_KEY=mb_xxx...

# customer-analytics/.env (module-specific)
CUSTOMER_ANALYTICS_ORDERS_CARD_ID=123

# sales-pipeline/.env (module-specific)
SALES_PIPELINE_DEALS_CARD_ID=456
```
✅ Single source of truth for credentials
✅ Update in one place
✅ Reduced security risk
✅ Module-specific card IDs

### Code Reuse

✅ Write once, use everywhere
✅ Bug fixes apply to all modules
✅ Consistent error handling
✅ Shared improvements benefit everyone

### Consistency

✅ Same API patterns across modules
✅ Same error messages and handling
✅ Same logging patterns
✅ Easier to maintain

---

## Adding New Shared Resources

To add a new shared resource:

1. Create the resource file in this directory:
   ```bash
   touch ~/workspace/patterns/dagster/shared-resources/my_resource.py
   ```

2. Follow the pattern from `metabase_resource.py`:
   - Use `ConfigurableResource` for the class
   - Use `@resource` decorator for the factory function
   - Include comprehensive docstrings and examples
   - Add error handling with `Failure` objects
   - Include metadata in all failures

3. Document in this README:
   - What it does
   - Environment variables required
   - Usage example
   - Benefits

4. Test in at least one module before marking stable

---

## Deployment Considerations

### Local Workspace

Shared resources work out-of-the-box in local workspace:
- Path is accessible: `~/workspace/patterns/`
- No additional configuration needed

### Production Deployment

When deploying to production (e.g., Yoda server):

**Option 1: Copy to module** (Simple, recommended for now)
```bash
cp ~/workspace/patterns/dagster/shared-resources/metabase_resource.py \
   ~/workspace/projects/my-module/src/my_module_dagster/resources/
```

Update imports:
```python
from .resources.metabase_resource import metabase_resource
```

**Option 2: Deploy patterns separately** (Future)
- Deploy `~/workspace/patterns/` to production
- Add to PYTHONPATH in production
- Keep imports as-is

**Option 3: Package as library** (Future, if many modules)
- Create `dagster-shared-resources` Python package
- Install in all modules
- Import from package

---

## Maintenance

### Versioning

Currently: No versioning (active development)

Future: Semantic versioning when stable
- Breaking changes: Major version
- New features: Minor version
- Bug fixes: Patch version

### Testing

Test changes to shared resources in at least one module before committing.

### Documentation

Keep this README updated when:
- Adding new resources
- Changing interfaces
- Updating environment variables
- Adding new deployment options

---

## Related Documentation

- **Module Pattern Guide**: See main documentation in this repository
- **Templates**: `~/workspace/patterns/dagster/`
- **Deployment Guide**: See PRODUCTION-DEPLOYMENT.md in this repository
