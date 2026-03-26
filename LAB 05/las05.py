import bpy
import math
import random
import os

TYPY_ROSLIN = {
    "drzewo": {
        "wysokosc": (3.0, 5.0),
        "liczba_lisci": (5, 10),
        "promien_lisci": (0.4, 0.7),
        "liczba_korzeni": (10, 15),
        "kolor_lodygi": (0.15, 0.08, 0.02, 1),
        "kolor_lisci": (0.05, 0.35, 0.1, 1),
    },
    "krzew": {
        "wysokosc": (0.8, 1.8),
        "liczba_lisci": (5, 8),
        "promien_lisci": (0.5, 0.9),
        "liczba_korzeni": (2, 4),
        "kolor_lodygi": (0.25, 0.15, 0.05, 1),
        "kolor_lisci": (0.1, 0.5, 0.05, 1),
    },
    "paproc": {
        "wysokosc": (0.5, 1.2),
        "liczba_lisci": (6, 10),
        "promien_lisci": (0.6, 1.0),
        "liczba_korzeni": (2, 3),
        "kolor_lodygi": (0.2, 0.3, 0.1, 1),
        "kolor_lisci": (0.0, 0.6, 0.15, 1),
    },
    "grzyb": {
        "wysokosc": (0.3, 0.7),
        "liczba_lisci": (0, 0),
        "promien_lisci": (0.0, 0.0),
        "liczba_korzeni": (0, 1),
        "kolor_lodygi": (0.9, 0.85, 0.7, 1),
        "kolor_lisci": (0.7, 0.1, 0.05, 1),
    },
}


def clean_scene():
    if bpy.ops.object.mode_set.poll():
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):
        if collection.name == "Las" or collection.name in {"Drzewa", "Krzewy", "Paprocie", "Grzyby"}:
            bpy.data.collections.remove(collection)

    for material in list(bpy.data.materials):
        if material.users == 0:
            bpy.data.materials.remove(material)

    for texture in list(bpy.data.textures):
        if texture.users == 0:
            bpy.data.textures.remove(texture)


def stworz_material(nazwa, kolor, roughness=0.5):
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = kolor
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def stworz_lodyge(location, height, radius, material):
    x, y, z = location
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        location=(x, y, z + height / 2)
    )
    obj = bpy.context.active_object
    obj.name = "Lodyga"
    if material:
        obj.data.materials.append(material)
    return obj


def stworz_liscie(location, height, num_leaves, radius_leaves, material, typ="drzewo"):
    x, y, z = location
    obiekty = []

    for i in range(num_leaves):
        angle = (2.5 * math.pi / max(1, num_leaves)) * i

        if typ == "drzewo":
            h = z + height * random.uniform(1.0, 0.6)
            dist = random.uniform(0.3, radius_leaves * 0.8)
        elif typ == "krzew":
            h = z + height * random.uniform(0.4, 0.9)
            dist = random.uniform(0.15, radius_leaves * 0.8)
        else:
            h = z + height * random.uniform(0.2, 0.5)
            dist = random.uniform(0, radius_leaves)

        lx = x + math.cos(angle) * dist
        ly = y + math.sin(angle) * dist

        tilt_x = random.uniform(0.2, 0.8)
        tilt_y = random.uniform(-0.3, 0.3)
        tilt_z = angle + random.uniform(-0.3, 0.3)

        bpy.ops.mesh.primitive_cube_add(
            size=radius_leaves,
            location=(lx, ly, h),
            rotation=(tilt_x, tilt_y, tilt_z)
        )
        obj = bpy.context.active_object
        obj.name = f"Lisc_{i}"

        if typ == "drzewo":
            obj.scale = (1.2, 0.4, 0.5)
        elif typ == "krzew":
            obj.scale = (0.9, 0.25, 0.15)
        else:
            obj.scale = (1.2, 0.18, 0.3)

        if material:
            obj.data.materials.append(material)

        obiekty.append(obj)

    return obiekty


def stworz_korzenie(location, num_roots, material):
    x, y, z = location
    obiekty = []

    for i in range(num_roots):
        angle = (2 * math.pi / max(1, num_roots)) * i
        dist = 0.25

        rx = x + math.cos(angle) * dist
        ry = y + math.sin(angle) * dist
        rz = z + 0.03

        bpy.ops.mesh.primitive_cube_add(
            size=0.3,
            location=(rx, ry, rz),
            rotation=(0.3, 0, angle)
        )
        obj = bpy.context.active_object
        obj.name = f"Korzen_{i}"
        obj.scale = (1.0, 0.25, 0.32)

        if material:
            obj.data.materials.append(material)

        obiekty.append(obj)

    return obiekty


def stworz_kapelusz_grzyba(location, height, material):
    x, y, z = location
    cap_z = z + height

    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=height * 0.6,
        location=(x, y, cap_z)
    )
    obj = bpy.context.active_object
    obj.name = "Kapelusz"
    obj.scale = (1.2, 1.2, 0.5)

    if material:
        obj.data.materials.append(material)

    return obj


def stworz_rosline(pozycja, wysokosc, liczba_lisci, promien_lisci,
                   liczba_korzeni, mat_lodyga, mat_lisci,
                   typ="drzewo", skala_globalna=1.0):
    obiekty = []

    wys = wysokosc * skala_globalna
    prom = promien_lisci * skala_globalna
    radius_stem = max(0.04, wysokosc * 0.035) * skala_globalna

    lodyga = stworz_lodyge(pozycja, wys, radius_stem, mat_lodyga)
    obiekty.append(lodyga)

    if typ == "grzyb":
        kapelusz = stworz_kapelusz_grzyba(pozycja, wys, mat_lisci)
        obiekty.append(kapelusz)
    else:
        liscie = stworz_liscie(pozycja, wys, liczba_lisci, prom, mat_lisci, typ=typ)
        obiekty.extend(liscie)

    if liczba_korzeni > 0 and typ != "grzyb":
        korzenie = stworz_korzenie(pozycja, liczba_korzeni, mat_lodyga)
        obiekty.extend(korzenie)

    return obiekty


def stworz_rosline_typ(x, y, typ, index=0):
    if typ not in TYPY_ROSLIN:
        print(f"Nieznany typ rośliny: {typ}")
        return []

    params = TYPY_ROSLIN[typ]

    wysokosc = random.uniform(*params["wysokosc"])
    liczba_lisci = random.randint(*params["liczba_lisci"])
    promien_lisci = random.uniform(*params["promien_lisci"])
    liczba_korzeni = random.randint(*params["liczba_korzeni"])
    skala_globalna = random.uniform(0.8, 1.3)

    def vary_color(base_color, variation=0.03):
        r = max(0, min(1, base_color[0] + random.uniform(-variation, variation)))
        g = max(0, min(1, base_color[1] + random.uniform(-variation, variation)))
        b = max(0, min(1, base_color[2] + random.uniform(-variation, variation)))
        return (r, g, b, base_color[3])

    kolor_lodygi = vary_color(params["kolor_lodygi"])
    kolor_lisci = vary_color(params["kolor_lisci"])

    mat_lodyga = stworz_material(f"Mat_{typ}_lodyga_{index}", kolor_lodygi, roughness=0.7)
    mat_lisci = stworz_material(f"Mat_{typ}_lisci_{index}", kolor_lisci, roughness=0.45)

    pozycja = (x, y, 0)

    obiekty = stworz_rosline(
        pozycja=pozycja,
        wysokosc=wysokosc,
        liczba_lisci=liczba_lisci,
        promien_lisci=promien_lisci,
        liczba_korzeni=liczba_korzeni,
        mat_lodyga=mat_lodyga,
        mat_lisci=mat_lisci,
        typ=typ,
        skala_globalna=skala_globalna
    )

    for obj in obiekty:
        obj.name = f"{typ}_{index}_{obj.name}"

    return obiekty


def wybierz_typ_biomu(x, y, rozmiar_pola, pozycje_drzew=None):
    polowa = rozmiar_pola / 2.0
    dystans_norm = max(abs(x), abs(y)) / polowa if polowa > 0 else 0

    if pozycje_drzew:
        for dx, dy in pozycje_drzew:
            odleglosc = math.sqrt((x - dx) ** 2 + (y - dy) ** 2)
            if odleglosc < 1.5 and random.random() < 0.35:
                return "grzyb"

    if dystans_norm < 0.3:
        return "drzewo"
    elif dystans_norm < 0.7:
        return "krzew" if random.random() < 0.7 else "drzewo"
    else:
        return "paproc" if random.random() < 0.65 else "krzew"


def stworz_teren(rozmiar_pola, kolekcja):
    bpy.ops.mesh.primitive_plane_add(
        size=rozmiar_pola * 1.3,
        location=(0, 0, 0)
    )
    teren = bpy.context.active_object
    teren.name = "Teren"

    mat_teren = stworz_material("Mat_Teren", (0.12, 0.08, 0.03, 1), roughness=0.95)
    teren.data.materials.append(mat_teren)

    bpy.ops.object.mode_set(mode='EDIT')
    for _ in range(5):
        bpy.ops.mesh.subdivide()
    bpy.ops.object.mode_set(mode='OBJECT')

    tex = bpy.data.textures.new("TerenTexture", type='CLOUDS')
    tex.noise_scale = 2.5

    mod = teren.modifiers.new(name="Displace", type='DISPLACE')
    mod.texture = tex
    mod.strength = 0.08
    mod.mid_level = 0.5

    for col in list(teren.users_collection):
        col.objects.unlink(teren)
    kolekcja.objects.link(teren)

    return teren


def znajdz_pozycje_roslin(liczba_roslin, rozmiar_pola, min_odstep=1.0, max_prob=500):
    pozycje = []
    polowa = rozmiar_pola / 2.0

    for _ in range(liczba_roslin):
        dodano = False

        for _ in range(max_prob):
            x = random.uniform(-polowa, polowa)
            y = random.uniform(-polowa, polowa)

            za_blisko = False
            for px, py in pozycje:
                if math.dist((x, y), (px, py)) < min_odstep:
                    za_blisko = True
                    break

            if not za_blisko:
                pozycje.append((x, y))
                dodano = True
                break

        if not dodano:
            x = random.uniform(-polowa, polowa)
            y = random.uniform(-polowa, polowa)
            pozycje.append((x, y))

    return pozycje


def generuj_las(liczba_roslin=40, rozmiar_pola=50.0, seed=42):
    random.seed(seed)

    clean_scene()

    kol_las = bpy.data.collections.new("Las")
    bpy.context.scene.collection.children.link(kol_las)

    podkolekcje = {}
    nazwy_podkolekcji = {
        "drzewo": "Drzewa",
        "krzew": "Krzewy",
        "paproc": "Paprocie",
        "grzyb": "Grzyby",
    }

    for typ, nazwa in nazwy_podkolekcji.items():
        podkol = bpy.data.collections.new(nazwa)
        kol_las.children.link(podkol)
        podkolekcje[typ] = podkol

    stworz_teren(rozmiar_pola, kol_las)

    pozycje = znajdz_pozycje_roslin(
        liczba_roslin=liczba_roslin,
        rozmiar_pola=rozmiar_pola,
        min_odstep=1.1
    )

    dane_roslin = []
    pozycje_drzew = []

    for i, (x, y) in enumerate(pozycje):
        typ = wybierz_typ_biomu(x, y, rozmiar_pola, pozycje_drzew=None)
        if typ == "drzewo":
            pozycje_drzew.append((x, y))
        dane_roslin.append((x, y, typ, i))

    for idx in range(len(dane_roslin)):
        x, y, typ, i = dane_roslin[idx]
        if typ != "drzewo":
            nowy_typ = wybierz_typ_biomu(x, y, rozmiar_pola, pozycje_drzew)
            dane_roslin[idx] = (x, y, nowy_typ, i)

    statystyki = {"drzewo": 0, "krzew": 0, "paproc": 0, "grzyb": 0}

    for x, y, typ, i in dane_roslin:
        obiekty = stworz_rosline_typ(x, y, typ, index=i)
        podkol = podkolekcje.get(typ, kol_las)

        for obj in obiekty:
            for col in list(obj.users_collection):
                col.objects.unlink(obj)
            podkol.objects.link(obj)

        statystyki[typ] += 1


    bpy.ops.object.light_add(type='SUN', location=(8, -8, 12))
    sun = bpy.context.active_object
    sun.name = "Slonce"
    sun.data.energy = 3.5
    sun.data.angle = 0.4
    sun.rotation_euler = (math.radians(50), math.radians(0), math.radians(35))
    for col in list(sun.users_collection):
        col.objects.unlink(sun)
    kol_las.objects.link(sun)

    bpy.ops.object.light_add(type='AREA', location=(0, -6, 7))
    area = bpy.context.active_object
    area.name = "Swiatlo_Obsarowe"
    area.data.energy = 250
    area.data.size = 10
    area.rotation_euler = (math.radians(65), 0, 0)
    for col in list(area.users_collection):
        col.objects.unlink(area)
    kol_las.objects.link(area)

    cam_dist = rozmiar_pola * 3.1
    bpy.ops.object.camera_add(location=(cam_dist * 0.65, -cam_dist * 0.9, cam_dist * 0.75))
    cam = bpy.context.active_object
    cam.name = "Kamera_Las"
    cam.rotation_euler = (math.radians(60), 0, math.radians(35))
    bpy.context.scene.camera = cam
    for col in list(cam.users_collection):
        col.objects.unlink(cam)
    kol_las.objects.link(cam)

    world = bpy.data.worlds.get("World")
    if world and world.use_nodes:
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.45, 0.60, 0.85, 1)
            bg.inputs["Strength"].default_value = 0.7

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.abspath("las_05.png")

    if hasattr(scene.eevee, 'use_gtao'):
        scene.eevee.use_gtao = True
    if hasattr(scene.eevee, 'gtao_distance'):
        scene.eevee.gtao_distance = 1.0
    if hasattr(scene.eevee, 'use_ssr'):
        scene.eevee.use_ssr = True
    if hasattr(scene.eevee, 'use_soft_shadows'):
        scene.eevee.use_soft_shadows = True

    bpy.ops.render.render(write_still=True)

    print(f"\n  Render zapisany: {scene.render.filepath}")
    print("=" * 60 + "\n")


generuj_las(liczba_roslin=500, rozmiar_pola=30.0, seed=42)