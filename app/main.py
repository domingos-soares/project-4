from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


ITEM_NOT_FOUND_DETAIL = "Item not found"


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


class InMemoryItemStore:
    def __init__(self) -> None:
        self._items: Dict[int, Item] = {}
        self._next_id: int = 1

    def list_items(self) -> List[Item]:
        return list(self._items.values())

    def get_item(self, item_id: int) -> Item:
        item = self._items.get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND_DETAIL)
        return item

    def create_item(self, item_in: ItemCreate) -> Item:
        item = Item(id=self._next_id, **item_in.dict())
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def update_item(self, item_id: int, item_in: ItemUpdate) -> Item:
        stored = self._items.get(item_id)
        if not stored:
            raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND_DETAIL)

        update_data = item_in.dict(exclude_unset=True)
        updated = stored.copy(update=update_data)
        self._items[item_id] = updated
        return updated

    def delete_item(self, item_id: int) -> None:
        if item_id not in self._items:
            raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND_DETAIL)
        del self._items[item_id]


app = FastAPI(title="Items Service", version="1.0.0")
store = InMemoryItemStore()


@app.get("/items", response_model=List[Item])
async def list_items() -> List[Item]:
    return store.list_items()


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    return store.get_item(item_id)


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item_in: ItemCreate) -> Item:
    return store.create_item(item_in)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_in: ItemUpdate) -> Item:
    return store.update_item(item_id, item_in)


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int) -> None:
    store.delete_item(item_id)
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
