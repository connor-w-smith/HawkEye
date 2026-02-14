


@router.get("/inventory/raw-materials/{finished_good_id}")
def read_raw_material_recipe_table(finished_good_id: str):
    try:
        data = get_raw_material_recipe(finished_good_id)
        return {"raw_materials": data}  # already a list of dicts
    except Exception:
        return {"raw_materials": []}