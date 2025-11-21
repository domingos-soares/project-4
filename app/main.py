from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Items Service", version="1.0.0")


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None


class Item(ItemBase):
    id: int


items_store: Dict[int, Item] = {}
next_id: int = 1


@app.get("/items", response_model=List[Item])
async def list_items() -> List[Item]:
    return list(items_store.values())


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    item = items_store.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item_in: ItemCreate) -> Item:
    global next_id
    item = Item(id=next_id, **item_in.dict())
    items_store[next_id] = item
    next_id += 1
    return item


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_in: ItemUpdate) -> Item:
    stored = items_store.get(item_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_in.dict(exclude_unset=True)
    updated = stored.copy(update=update_data)
    items_store[item_id] = updated
    return updated


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int) -> None:
    if item_id not in items_store:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_store[item_id]
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
