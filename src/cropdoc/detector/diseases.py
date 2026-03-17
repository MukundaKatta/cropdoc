"""Disease database containing 16 plant diseases with full details."""

from __future__ import annotations

from cropdoc.models import Disease


class DiseaseDatabase:
    """Comprehensive database of crop diseases with symptoms, treatments, and prevention."""

    def __init__(self) -> None:
        self._diseases: dict[str, Disease] = {}
        self._build_database()

    def _build_database(self) -> None:
        entries = [
            Disease(
                name="Tomato Early Blight",
                scientific_name="Alternaria solani",
                crop="tomato",
                pathogen_type="fungal",
                symptoms=[
                    "Dark concentric rings on lower leaves (target-spot pattern)",
                    "Yellowing around lesions",
                    "Premature leaf drop starting from base",
                    "Dark sunken lesions on stems",
                ],
                treatment_organic=[
                    "Neem oil spray (2% solution) every 7-10 days",
                    "Copper-based fungicide (Bordeaux mixture)",
                    "Bacillus subtilis biological fungicide",
                    "Remove and destroy infected foliage",
                ],
                treatment_chemical=[
                    "Chlorothalonil (Daconil) every 7-14 days",
                    "Mancozeb 75% WP at 2g/L",
                    "Azoxystrobin (Quadris) at first sign of disease",
                ],
                prevention=[
                    "Rotate crops on a 3-year cycle",
                    "Mulch around base to prevent soil splash",
                    "Water at base, avoid wetting foliage",
                    "Ensure adequate plant spacing for air circulation",
                ],
                spread_rate=0.6,
            ),
            Disease(
                name="Tomato Late Blight",
                scientific_name="Phytophthora infestans",
                crop="tomato",
                pathogen_type="fungal",
                symptoms=[
                    "Water-soaked gray-green spots on leaves",
                    "White fuzzy mold on leaf undersides in humid conditions",
                    "Rapid browning and wilting of foliage",
                    "Firm dark lesions on fruit",
                ],
                treatment_organic=[
                    "Copper hydroxide spray at 2-3 day intervals",
                    "Remove and destroy all infected tissue immediately",
                    "Bacillus amyloliquefaciens preventive spray",
                ],
                treatment_chemical=[
                    "Metalaxyl-M (Ridomil Gold) systemic fungicide",
                    "Cymoxanil + Mancozeb combination",
                    "Mandipropamid (Revus) every 7 days",
                ],
                prevention=[
                    "Use certified disease-free seed and transplants",
                    "Destroy volunteer tomato and potato plants",
                    "Improve drainage to reduce standing water",
                    "Monitor weather for blight-favorable conditions",
                ],
                spread_rate=0.9,
            ),
            Disease(
                name="Tomato Leaf Mold",
                scientific_name="Passalora fulva",
                crop="tomato",
                pathogen_type="fungal",
                symptoms=[
                    "Pale green to yellowish spots on upper leaf surface",
                    "Olive-green to brown velvety mold on leaf undersides",
                    "Leaves curl, wither, and drop prematurely",
                    "Primarily affects greenhouse-grown tomatoes",
                ],
                treatment_organic=[
                    "Improve ventilation and reduce humidity below 85%",
                    "Potassium bicarbonate spray",
                    "Sulfur-based fungicide applications",
                ],
                treatment_chemical=[
                    "Difenoconazole (Score) at 0.5ml/L",
                    "Chlorothalonil preventive sprays",
                ],
                prevention=[
                    "Maintain greenhouse humidity below 85%",
                    "Use resistant tomato varieties (Cf gene cultivars)",
                    "Space plants for adequate air movement",
                    "Avoid overhead irrigation",
                ],
                spread_rate=0.5,
            ),
            Disease(
                name="Potato Early Blight",
                scientific_name="Alternaria solani",
                crop="potato",
                pathogen_type="fungal",
                symptoms=[
                    "Small dark spots with concentric rings on older leaves",
                    "Lesions may coalesce covering large leaf areas",
                    "Premature defoliation reducing tuber yield",
                    "Shallow dark lesions on tubers",
                ],
                treatment_organic=[
                    "Copper-based fungicides (copper sulfate)",
                    "Trichoderma harzianum biological control",
                    "Remove infected plant debris promptly",
                ],
                treatment_chemical=[
                    "Mancozeb 75% WP at 2.5g/L biweekly",
                    "Azoxystrobin (Amistar) at tuber initiation",
                    "Boscalid + Pyraclostrobin (Pristine)",
                ],
                prevention=[
                    "Use certified seed potatoes",
                    "Hill soil around plants to protect tubers",
                    "Maintain balanced fertilization (avoid excess nitrogen)",
                    "Harvest tubers at full maturity",
                ],
                spread_rate=0.55,
            ),
            Disease(
                name="Potato Late Blight",
                scientific_name="Phytophthora infestans",
                crop="potato",
                pathogen_type="fungal",
                symptoms=[
                    "Large irregular water-soaked lesions on leaves",
                    "White sporulation on leaf undersides",
                    "Stems develop dark brown lesions",
                    "Tubers show reddish-brown granular rot",
                ],
                treatment_organic=[
                    "Copper hydroxide at 1.5-2g/L every 5-7 days",
                    "Destroy all infected plants and tubers",
                    "Bacillus subtilis preventive applications",
                ],
                treatment_chemical=[
                    "Metalaxyl-M + Mancozeb (Ridomil Gold MZ)",
                    "Cymoxanil + Famoxadone (Tanos)",
                    "Fluopicolide (Infinito) systemic treatment",
                ],
                prevention=[
                    "Plant resistant varieties (R-gene cultivars)",
                    "Eliminate cull piles and volunteer potatoes",
                    "Monitor with blight forecasting systems",
                    "Destroy haulms 2-3 weeks before harvest",
                ],
                spread_rate=0.95,
            ),
            Disease(
                name="Corn Northern Leaf Blight",
                scientific_name="Exserohilum turcicum",
                crop="corn",
                pathogen_type="fungal",
                symptoms=[
                    "Long elliptical gray-green lesions (2.5-15cm) on leaves",
                    "Lesions start on lower leaves and progress upward",
                    "Heavy infection causes premature leaf death",
                    "Reduced grain fill and ear development",
                ],
                treatment_organic=[
                    "Trichoderma-based biological fungicides",
                    "Remove and destroy crop residue after harvest",
                    "Crop rotation with non-host species",
                ],
                treatment_chemical=[
                    "Propiconazole (Tilt) at tassel emergence",
                    "Azoxystrobin + Propiconazole (Quilt Xcel)",
                    "Pyraclostrobin (Headline) single application",
                ],
                prevention=[
                    "Plant resistant hybrids with Ht genes",
                    "Rotate corn with soybeans or small grains",
                    "Tillage to bury infected residue",
                    "Avoid continuous corn planting",
                ],
                spread_rate=0.6,
            ),
            Disease(
                name="Corn Common Rust",
                scientific_name="Puccinia sorghi",
                crop="corn",
                pathogen_type="fungal",
                symptoms=[
                    "Small circular to elongated reddish-brown pustules",
                    "Pustules appear on both leaf surfaces",
                    "Rupture releasing powdery reddish-brown spores",
                    "Severe cases cause leaf yellowing and necrosis",
                ],
                treatment_organic=[
                    "Sulfur dust applications at early infection",
                    "Neem oil sprays for mild infections",
                    "Remove heavily infected plants",
                ],
                treatment_chemical=[
                    "Triazole fungicides (propiconazole, tebuconazole)",
                    "Strobilurin fungicides (azoxystrobin)",
                    "Mancozeb protective sprays",
                ],
                prevention=[
                    "Plant resistant hybrids (Rp gene resistance)",
                    "Early planting to avoid peak spore seasons",
                    "Scout fields regularly starting at V8 stage",
                    "Balanced fertilization program",
                ],
                spread_rate=0.7,
            ),
            Disease(
                name="Apple Scab",
                scientific_name="Venturia inaequalis",
                crop="apple",
                pathogen_type="fungal",
                symptoms=[
                    "Olive-green to dark brown velvety lesions on leaves",
                    "Lesions on fruit become corky and cracked",
                    "Premature leaf and fruit drop",
                    "Distorted fruit growth in severe cases",
                ],
                treatment_organic=[
                    "Sulfur sprays during early spring",
                    "Lime sulfur during dormant season",
                    "Potassium bicarbonate foliar spray",
                    "Rake and destroy fallen leaves in autumn",
                ],
                treatment_chemical=[
                    "Captan 50% WP at 2g/L during bloom",
                    "Myclobutanil (Rally) systemic fungicide",
                    "Dodine (Syllit) pre-bloom application",
                ],
                prevention=[
                    "Plant scab-resistant apple varieties",
                    "Prune trees for open canopy and air circulation",
                    "Apply urea to fallen leaves to speed decomposition",
                    "Remove water sprouts and suckers",
                ],
                spread_rate=0.65,
            ),
            Disease(
                name="Cedar Apple Rust",
                scientific_name="Gymnosporangium juniperi-virginianae",
                crop="apple",
                pathogen_type="fungal",
                symptoms=[
                    "Bright orange-yellow spots on upper leaf surface",
                    "Tube-like structures (aecia) on leaf undersides",
                    "Spots may appear on fruit causing deformity",
                    "Premature defoliation in severe infections",
                ],
                treatment_organic=[
                    "Remove nearby juniper/cedar alternate hosts within 1 mile",
                    "Sulfur fungicide during spring rains",
                    "Neem oil applications every 7-10 days",
                ],
                treatment_chemical=[
                    "Myclobutanil (Rally) at pink bud stage",
                    "Fenarimol (Rubigan) systemic fungicide",
                    "Triadimefon (Bayleton) applications",
                ],
                prevention=[
                    "Plant rust-resistant apple cultivars",
                    "Remove galls from juniper hosts in winter",
                    "Maintain distance from eastern red cedar trees",
                    "Monitor in spring during warm rainy periods",
                ],
                spread_rate=0.4,
            ),
            Disease(
                name="Grape Black Rot",
                scientific_name="Guignardia bidwellii",
                crop="grape",
                pathogen_type="fungal",
                symptoms=[
                    "Circular reddish-brown leaf spots with dark borders",
                    "Black pycnidia visible in lesion centers",
                    "Berries turn brown then shrivel into hard black mummies",
                    "Shoot lesions appear as dark elongated cankers",
                ],
                treatment_organic=[
                    "Remove mummified fruit and infected canes during pruning",
                    "Copper-based sprays at bud break",
                    "Sulfur applications during growing season",
                ],
                treatment_chemical=[
                    "Myclobutanil (Rally) from bloom to veraison",
                    "Mancozeb pre-bloom applications",
                    "Captan + Myclobutanil rotation program",
                ],
                prevention=[
                    "Sanitation: remove all mummies and infected debris",
                    "Open canopy management for air circulation",
                    "Train vines for good sun exposure",
                    "Timely fungicide program from bud break to veraison",
                ],
                spread_rate=0.7,
            ),
            Disease(
                name="Grape Esca (Black Measles)",
                scientific_name="Phaeomoniella chlamydospora complex",
                crop="grape",
                pathogen_type="fungal",
                symptoms=[
                    "Tiger-stripe pattern of chlorosis between leaf veins",
                    "Dark spotting on berries (measles appearance)",
                    "Sudden wilting and death of shoots (apoplexy)",
                    "Cross-section of wood shows dark streaking",
                ],
                treatment_organic=[
                    "Trichoderma-based wound protectants after pruning",
                    "Sodium arsenite trunk injection (restricted use)",
                    "Remove and destroy severely affected vines",
                ],
                treatment_chemical=[
                    "Thiophanate-methyl wound treatment",
                    "Fosetyl-aluminum trunk applications",
                    "No fully effective chemical treatment exists",
                ],
                prevention=[
                    "Prune in late dormancy to minimize wound exposure",
                    "Apply wound sealant immediately after pruning cuts",
                    "Use disease-free propagation material",
                    "Avoid large pruning wounds on cordons and trunk",
                ],
                spread_rate=0.3,
            ),
            Disease(
                name="Citrus Canker",
                scientific_name="Xanthomonas citri subsp. citri",
                crop="citrus",
                pathogen_type="bacterial",
                symptoms=[
                    "Raised corky brown lesions with water-soaked margins",
                    "Yellow halo surrounding lesions on leaves",
                    "Crater-like lesions on fruit surface",
                    "Premature fruit drop and defoliation",
                ],
                treatment_organic=[
                    "Copper hydroxide sprays every 21 days",
                    "Bordeaux mixture applications",
                    "Prune and burn infected branches",
                ],
                treatment_chemical=[
                    "Copper oxychloride + Streptomycin combination",
                    "Copper ammonium acetate foliar sprays",
                    "Kasugamycin (Kasumin) bactericide",
                ],
                prevention=[
                    "Use canker-free nursery stock",
                    "Windbreaks to reduce wind-driven rain spread",
                    "Disinfect pruning tools between trees",
                    "Quarantine and destroy severely infected trees",
                ],
                spread_rate=0.75,
            ),
            Disease(
                name="Citrus Huanglongbing (Greening)",
                scientific_name="Candidatus Liberibacter asiaticus",
                crop="citrus",
                pathogen_type="bacterial",
                symptoms=[
                    "Asymmetric blotchy mottling of leaves (unlike nutrient deficiency)",
                    "Small lopsided fruit with aborted seeds",
                    "Fruit remains green at the stylar end",
                    "Twig dieback and overall tree decline",
                ],
                treatment_organic=[
                    "Nutritional supplementation (foliar micronutrients)",
                    "Thermotherapy (heat treatment of young trees)",
                    "Biological control of Asian citrus psyllid vector",
                ],
                treatment_chemical=[
                    "Imidacloprid soil drench for psyllid control",
                    "Oxytetracycline trunk injection (experimental)",
                    "Spirotetramat (Movento) for psyllid management",
                ],
                prevention=[
                    "Use disease-free certified nursery stock",
                    "Aggressive psyllid vector management program",
                    "Scout regularly and remove infected trees promptly",
                    "Screen nurseries to exclude psyllid vectors",
                ],
                spread_rate=0.85,
            ),
            Disease(
                name="Rice Blast",
                scientific_name="Magnaporthe oryzae",
                crop="rice",
                pathogen_type="fungal",
                symptoms=[
                    "Diamond-shaped lesions with gray centers on leaves",
                    "Neck rot causing panicle breakage (neck blast)",
                    "Node infections turning black",
                    "White panicles due to incomplete grain filling",
                ],
                treatment_organic=[
                    "Silicon-based fertilizers to strengthen cell walls",
                    "Trichoderma viride seed treatment",
                    "Pseudomonas fluorescens foliar application",
                ],
                treatment_chemical=[
                    "Tricyclazole (Beam) preventive spray at booting",
                    "Isoprothiolane (Fuji-one) at 1.5ml/L",
                    "Carbendazim 50% WP at 1g/L",
                ],
                prevention=[
                    "Plant blast-resistant varieties (Pi gene cultivars)",
                    "Avoid excess nitrogen fertilization",
                    "Maintain adequate flooding to reduce spore release",
                    "Balanced potassium and phosphorus nutrition",
                ],
                spread_rate=0.8,
            ),
            Disease(
                name="Rice Brown Spot",
                scientific_name="Bipolaris oryzae",
                crop="rice",
                pathogen_type="fungal",
                symptoms=[
                    "Oval brown spots with gray centers on leaves",
                    "Spots on leaf sheaths, glumes, and grains",
                    "Seedling blight in nurseries",
                    "Grain discoloration reducing quality and yield",
                ],
                treatment_organic=[
                    "Seed treatment with Pseudomonas fluorescens",
                    "Trichoderma viride at 4g/kg seed",
                    "Improve soil fertility with organic matter",
                ],
                treatment_chemical=[
                    "Propiconazole (Tilt) at 1ml/L",
                    "Edifenphos (Hinosan) at 1ml/L",
                    "Mancozeb 75% WP at 2.5g/L",
                ],
                prevention=[
                    "Use disease-free seed from healthy fields",
                    "Balanced fertilization especially potassium",
                    "Maintain proper soil pH (5.5-6.5)",
                    "Avoid nutrient-stressed conditions",
                ],
                spread_rate=0.5,
            ),
            Disease(
                name="Wheat Rust",
                scientific_name="Puccinia triticina",
                crop="wheat",
                pathogen_type="fungal",
                symptoms=[
                    "Orange-brown circular pustules on leaf surfaces",
                    "Pustules rupture releasing masses of urediniospores",
                    "Severe infection causes leaf death and shriveled grain",
                    "Different rust types: leaf rust, stem rust, stripe rust",
                ],
                treatment_organic=[
                    "Plant resistant varieties as primary strategy",
                    "Early planting to escape peak rust pressure",
                    "Balanced nutrition to promote plant vigor",
                ],
                treatment_chemical=[
                    "Tebuconazole (Folicur) at flag leaf stage",
                    "Propiconazole + Cyproconazole at 0.5L/ha",
                    "Epoxiconazole (Opus) preventive spray",
                ],
                prevention=[
                    "Deploy varieties with adult plant resistance (APR)",
                    "Diversify rust resistance genes across region",
                    "Eliminate volunteer wheat and alternate hosts",
                    "Monitor for new virulent rust races",
                ],
                spread_rate=0.85,
            ),
        ]
        for disease in entries:
            self._diseases[disease.name] = disease

    @property
    def all_diseases(self) -> list[Disease]:
        """Return all diseases in the database."""
        return list(self._diseases.values())

    @property
    def disease_names(self) -> list[str]:
        """Return all disease names."""
        return list(self._diseases.keys())

    @property
    def supported_crops(self) -> list[str]:
        """Return unique crop types."""
        return sorted({d.crop for d in self._diseases.values()})

    def get(self, name: str) -> Disease | None:
        """Look up a disease by exact name."""
        return self._diseases.get(name)

    def search(self, query: str) -> list[Disease]:
        """Search diseases by name substring (case-insensitive)."""
        q = query.lower()
        return [d for d in self._diseases.values() if q in d.name.lower()]

    def by_crop(self, crop: str) -> list[Disease]:
        """Get all diseases for a given crop."""
        c = crop.lower()
        return [d for d in self._diseases.values() if d.crop.lower() == c]

    def by_pathogen_type(self, pathogen_type: str) -> list[Disease]:
        """Get all diseases caused by a given pathogen type."""
        pt = pathogen_type.lower()
        return [
            d for d in self._diseases.values()
            if d.pathogen_type.lower() == pt
        ]

    def get_by_index(self, index: int) -> Disease:
        """Get disease by its index in the database."""
        diseases = self.all_diseases
        return diseases[index % len(diseases)]
