from fastapi import FastAPI, HTTPException, Response, status

from model import Product

app = FastAPI()


products_list = {
    0: Product(
        sku="GA04834-US",
        name="Pixel 8",
        description="The Google Pixel 8 Pro is a top-of-the-line phone with a big screen, super-fast processor, and amazing camera.",
        in_stock=True,
    ),
    1: Product(
        sku="AP1234-US",
        name="iPhone 15 Plus",
        description="Apple"
        "s latest large-screen iPhone with a powerful A17 Bionic chip and an advanced camera system for stunning photos and videos.",
        in_stock=True,
    ),
    2: Product(
        sku="SM5678-US",
        name="Galaxy S24 Ultra",
        description="Samsung"
        "s powerhouse phone with a massive, gorgeous display, a super-fast processor for smooth gaming, and versatile cameras that excel in any lighting.",
        in_stock=False,
    ),
    3: Product(
        sku="OP9012-US",
        name="OnePlus 12 Pro",
        description="A lightning-fast phone with a large, immersive display for a great price. The OnePlus 12 Pro boasts a powerful processor and a capable camera system.",
        in_stock=True,
    ),
    4: Product(
        sku="RZ8888-US",
        name="Razor Phone 7",
        description="The Razor Phone 7 is a gaming phone with a high refresh rate display for ultra-smooth visuals, a powerful processor for demanding games, and a long-lasting battery to keep you powered through extended gaming sessions.",
        in_stock=False,
    ),
}


@app.get("/")
def index():
    return Response("Server running")


@app.get("/products/")
async def products():
    return products_list


@app.get("/products/name/{product_name:str}")
async def query_product_by_name(product_name: str) -> Product:
    """ """
    for _, product in products_list.items():

        if product_name.lower() == product.name.lower():
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with name={product_name} not found.",
    )


@app.get("/products/{product_id:int}")
def query_product_by_id(product_id: int) -> Product:
    """ """
    if product_id not in products_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with sku={product_id} not found.",
        )
    return products_list[product_id]
