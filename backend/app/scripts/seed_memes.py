"""
Grasschalant — Meme Vault Seeder
Seeds ~1,500 curated meme archetype templates into MongoDB Atlas grasschalant.meme_vault
with CLIP embeddings for vector search.

Usage:
    cd backend
    python -m app.scripts.seed_memes
"""

import asyncio
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add parent dirs to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from app.services.embedder import embed_texts_batch

# ═══════════════════════════════════════════════════════════════════════════════
# MEME ARCHETYPE CATALOG
# Each entry: (name, description/visual_tags, image_url, category)
# We use popular, widely-recognized meme templates with their imgflip/knowyourmeme CDN URLs
# ═══════════════════════════════════════════════════════════════════════════════

MEME_ARCHETYPES = [
    # ── REACTION FACES ─────────────────────────────────────────────────────────
    ("Surprised Pikachu", "shocked yellow face with wide open mouth and round eyes, electric mouse surprised expression", "https://i.imgflip.com/2kbn1e.jpg", "reaction"),
    ("Distracted Boyfriend", "man turning to look at another woman while his girlfriend looks on disapprovingly, betrayal jealousy choice", "https://i.imgflip.com/1ur9b0.jpg", "reaction"),
    ("Side Eye Chloe", "little girl giving suspicious skeptical side glance, doubt disbelief judging look", "https://i.imgflip.com/1ihzfe.jpg", "reaction"),
    ("Roll Safe", "man tapping temple with finger pointing at head, clever thinking smart logic cant fail", "https://i.imgflip.com/1h7in3.jpg", "reaction"),
    ("Confused Nick Young", "basketball player with question marks around head, bewildered puzzled expression", "https://i.imgflip.com/1otk96.jpg", "reaction"),
    ("Blinking White Guy", "man blinking in disbelief, slow realization shock processing", "https://i.imgflip.com/1w7yia.jpg", "reaction"),
    ("Woman Yelling at Cat", "angry woman pointing at confused white cat sitting at dinner table, confrontation argument", "https://i.imgflip.com/345v97.jpg", "reaction"),
    ("Leonardo DiCaprio Laughing", "man laughing while holding a drink, amused reaction from Django Unchained", "https://i.imgflip.com/26jxvz.jpg", "reaction"),
    ("Arthur Fist", "cartoon aardvark clenching fist in anger, barely contained rage frustration", "https://i.imgflip.com/11wv68.jpg", "reaction"),
    ("Crying Wojak", "simple drawn face crying with tears streaming down, sadness despair mask", "https://i.imgflip.com/4acd7j.jpg", "reaction"),
    ("Gigachad", "extremely muscular handsome man with chiseled jaw, ultimate confidence superiority", "https://i.imgflip.com/5dnv1l.jpg", "reaction"),
    ("Megamind No Bitches", "blue alien supervillain asking no bitches, loneliness relationship humor", "https://i.imgflip.com/64sz4u.jpg", "reaction"),
    ("This Is Fine Dog", "cartoon dog sitting in burning room drinking coffee, calm amid chaos", "https://i.imgflip.com/wxica.jpg", "reaction"),
    ("Panik Kalm Panik", "three panel meme man showing panic then calm then panic again, escalating anxiety", "https://i.imgflip.com/3qqcim.jpg", "reaction"),
    ("Sad Pablo Escobar", "man standing alone on balcony looking sad waiting, lonely contemplation", "https://i.imgflip.com/33f3y2.jpg", "reaction"),
    ("Mr Incredible Becoming Uncanny", "cartoon dad face transforming from happy to increasingly disturbing, progressively worse", "https://i.imgflip.com/5wdwcy.jpg", "reaction"),
    ("Pedro Pascal Crying Laughing", "actor alternating between crying and laughing uncontrollably, emotional whiplash", "https://i.imgflip.com/7nnl7c.jpg", "reaction"),
    ("Drake Hotline Bling", "man rejecting one option and approving another, preference choice comparison", "https://i.imgflip.com/30b1gx.jpg", "reaction"),
    ("Monkey Puppet Side Eye", "puppet monkey looking away nervously with side glance, guilty awkward avoidance", "https://i.imgflip.com/2gnnjh.jpg", "reaction"),
    ("Michael Scott No", "office manager screaming no dramatically, refusal denial extreme reaction", "https://i.imgflip.com/t4qfm.jpg", "reaction"),

    # ── ANIMALS ────────────────────────────────────────────────────────────────
    ("Doge", "shiba inu dog with internal monologue, such wow much amaze very interest", "https://i.imgflip.com/4t0m5.jpg", "animal"),
    ("Cheems", "chubby doge with speech impediment, bonk horny police bat", "https://i.imgflip.com/3nk5yf.jpg", "animal"),
    ("Grumpy Cat", "cat with perpetually angry frowning face, displeasure disapproval sourpuss", "https://i.imgflip.com/gk5el.jpg", "animal"),
    ("Cat Vibing", "white cat nodding head rhythmically to music, groove enjoying beat", "https://i.imgflip.com/4bh8d8.jpg", "animal"),
    ("Polite Cat", "cat smiling politely at camera, awkward smile forced politeness", "https://i.imgflip.com/2wifhj.jpg", "animal"),
    ("Buff Doge vs Cheems", "muscular ancient doge compared to wimpy modern doge, past vs present decline", "https://i.imgflip.com/43a45p.jpg", "animal"),
    ("I Should Buy A Boat Cat", "cat in business suit reading newspaper thoughtfully, sudden life ambition", "https://i.imgflip.com/5x14y.jpg", "animal"),
    ("Cat Loading", "cat staring blankly with buffering wheel, processing information slowly brain lag", "https://i.imgflip.com/2cp1ly.jpg", "animal"),
    ("Dramatic Chipmunk", "chipmunk turning dramatically toward camera with suspenseful music, reveal moment", "https://i.imgflip.com/9vct.jpg", "animal"),
    ("Spider-Man Pointing", "two identical spider-men pointing at each other, accusation hypocrisy identical", "https://i.imgflip.com/1tkjq9.jpg", "animal"),
    ("Business Cat", "cat wearing tiny business tie looking serious, corporate feline authority", "https://i.imgflip.com/i0sih.jpg", "animal"),
    ("Seal of Approval", "happy baby seal clapping flippers, excited celebrating good news", "https://i.imgflip.com/oe3fv.jpg", "animal"),
    ("Penguin Slap", "penguin slapping another penguin, unexpected attack betrayal", "https://i.imgflip.com/3w0z7h.jpg", "animal"),
    ("Disaster Girl", "young girl smiling menacingly in front of burning house, evil satisfaction chaos", "https://i.imgflip.com/23ls.jpg", "animal"),
    ("Crying Cat", "cat with teary eyes looking sad, depression sadness feline tears", "https://i.imgflip.com/2t3zfg.jpg", "animal"),
    ("Screaming Cat", "cat with mouth wide open screaming, shock horror terror feline", "https://i.imgflip.com/3h7em2.jpg", "animal"),
    ("Long Cat", "extremely elongated white cat being held up, stretching infinity length", "https://i.imgflip.com/3otr.jpg", "animal"),
    ("Ceiling Cat", "cat peering through hole in ceiling watching from above, surveillance big brother", "https://i.imgflip.com/4tyh.jpg", "animal"),
    ("Nyan Cat", "pixel art cat with rainbow trail flying through space, pop tart body chiptune music", "https://i.imgflip.com/1bff.jpg", "animal"),
    ("Angry Cat", "cat hissing aggressively with ears back, fury rage attack mode", "https://i.imgflip.com/1p3jrb.jpg", "animal"),

    # ── SPONGEBOB & CARTOONS ──────────────────────────────────────────────────
    ("Mocking SpongeBob", "sponge character standing in distorted mocking pose, alternating caps sarcasm", "https://i.imgflip.com/1otk96.jpg", "cartoon"),
    ("Imagination SpongeBob", "yellow sponge creating rainbow with hands, showing possibility and wonder", "https://i.imgflip.com/1d31.jpg", "cartoon"),
    ("Two Buttons", "superhero sweating over two red buttons, impossible choice dilemma", "https://i.imgflip.com/1g8my4.jpg", "cartoon"),
    ("Expanding Brain", "four panel brain progressively glowing larger and more cosmic, escalating intelligence", "https://i.imgflip.com/1jwhww.jpg", "cartoon"),
    ("Is This a Pigeon", "anime man pointing at butterfly asking if it is a pigeon, misidentification confusion", "https://i.imgflip.com/1o00in.jpg", "cartoon"),
    ("Tom and Jerry Newspaper", "cartoon cat reading newspaper with smug expression, ignoring problems", "https://i.imgflip.com/3e0e3.jpg", "cartoon"),
    ("Squidward Window", "squidward looking out window sadly at others having fun, exclusion jealousy", "https://i.imgflip.com/19vcz0.jpg", "cartoon"),
    ("Patrick Star Smart Wallet", "starfish holding up wallet showing id, no this is patrick", "https://i.imgflip.com/1gpc3x.jpg", "cartoon"),
    ("Skinner Out of Touch", "principal skinner asking am I out of touch no its the children, denial boomer", "https://i.imgflip.com/2bntw3.jpg", "cartoon"),
    ("Homer Simpson Bush", "man slowly backing into hedge to disappear, retreat avoiding confrontation", "https://i.imgflip.com/38el5u.jpg", "cartoon"),
    ("Tuxedo Winnie Pooh", "bear character in tuxedo looking sophisticated vs normal bear, fancy vs casual", "https://i.imgflip.com/2ybua0.jpg", "cartoon"),
    ("Bugs Bunny Communism", "cartoon rabbit presenting communism our meme, sharing collectivism", "https://i.imgflip.com/2e7a1a.jpg", "cartoon"),
    ("Handshake Meme", "two muscular arms clasping hands in agreement, unlikely alliance common ground", "https://i.imgflip.com/1nck6k.jpg", "cartoon"),
    ("Gru Plan", "villain presenting plan on board then realizing flaw, backfired scheme", "https://i.imgflip.com/26jxvz.jpg", "cartoon"),
    ("Brain Expansion Galaxy", "brain going from small to galactic universal enlightenment, transcendence", "https://i.imgflip.com/4a0vsi.jpg", "cartoon"),
    ("Shrek Face", "ogre smiling knowingly layers like onion, it is all ogre now intimacy", "https://i.imgflip.com/1bij.jpg", "cartoon"),
    ("Patrick Star Mayonnaise", "is mayonnaise an instrument question, absurd inquiry stupidity charm", "https://i.imgflip.com/2w7b2a.jpg", "cartoon"),
    ("Thanos Snap", "purple titan snapping fingers, inevitable balanced as things should be", "https://i.imgflip.com/28j0te.jpg", "cartoon"),
    ("Thanos Impossible", "purple titan shocked saying impossible, disbelief at unlikely outcome", "https://i.imgflip.com/2r6u8z.jpg", "cartoon"),
    ("I See No God Up Here Other Than Me", "cat sitting atop high place looking down with divine confidence", "https://i.imgflip.com/3k3epj.jpg", "cartoon"),

    # ── FEELINGS & SITUATIONS ─────────────────────────────────────────────────
    ("Change My Mind", "man sitting at table with sign challenge, debate invitation prove me wrong", "https://i.imgflip.com/24y43o.jpg", "situation"),
    ("Left Exit 12 Off Ramp", "car swerving at last second to take highway exit, sudden decision change", "https://i.imgflip.com/1qh8vu.jpg", "situation"),
    ("Running Away Balloon", "man chasing balloon that keeps floating away, losing grip on things", "https://i.imgflip.com/392xtu.jpg", "situation"),
    ("Always Has Been", "astronaut pointing gun at another astronaut in space, it was always this way", "https://i.imgflip.com/46e43q.jpg", "situation"),
    ("Domino Effect", "tiny domino knocking over progressively larger dominoes, chain reaction escalation", "https://i.imgflip.com/4n0tl0.jpg", "situation"),
    ("Trade Offer", "man making trade offer deal, I receive you receive negotiation", "https://i.imgflip.com/54hjww.jpg", "situation"),
    ("I Dont Always", "most interesting man in world drinking beer, sophisticated conditional statement", "https://i.imgflip.com/1bip.jpg", "situation"),
    ("First Time", "man about to be hanged saying first time casually, veterans perspective", "https://i.imgflip.com/3pnmg.jpg", "situation"),
    ("Bernie I Am Once Again Asking", "man in mittens asking for financial support once again, persistent request", "https://i.imgflip.com/3oevdk.jpg", "situation"),
    ("Kermit Looking Out Window", "frog staring out rainy window contemplatively, none of my business sipping tea", "https://i.imgflip.com/19mid.jpg", "situation"),
    ("Oprah You Get A", "talk show host excitedly giving things to everyone, generous distribution", "https://i.imgflip.com/pflw.jpg", "situation"),
    ("Matrix Red Blue Pill", "choosing between two pills, truth vs comfortable ignorance", "https://i.imgflip.com/z6fq.jpg", "situation"),
    ("Sleeping Shaq", "man sleeping through first event then wide awake for second, selective attention", "https://i.imgflip.com/21aqbc.jpg", "situation"),
    ("Wait Its All Ohio", "astronaut looking at earth and its all Ohio, the truth was mundane", "https://i.imgflip.com/4ayo73.jpg", "situation"),
    ("UNO Draw 25", "man choosing to draw 25 UNO cards rather than do something, extreme avoidance", "https://i.imgflip.com/3lmzyx.jpg", "situation"),
    ("They Dont Know", "person standing alone at party while others dance, internal monologue superiority", "https://i.imgflip.com/4ecbya.jpg", "situation"),
    ("Futurama Shut Up Take My Money", "man throwing money at screen wanting product immediately, impulse buy", "https://i.imgflip.com/3si4.jpg", "situation"),
    ("One Does Not Simply", "man explaining difficulty of task, its not that simple lord of rings", "https://i.imgflip.com/1bij.jpg", "situation"),
    ("Say The Line Bart", "classroom pressuring student to repeat famous catchphrase, predictable demand", "https://i.imgflip.com/1e7ql7.jpg", "situation"),
    ("Corporate Needs You To Find Difference", "woman holding two pictures asking to find difference they are same, identical indistinguishable", "https://i.imgflip.com/2za3u1.jpg", "situation"),

    # ── EMOTIONAL STATES ──────────────────────────────────────────────────────
    ("Hide The Pain Harold", "older man smiling through obvious internal pain, masking suffering with grin", "https://i.imgflip.com/gk5el.jpg", "emotion"),
    ("Sad Keanu", "man sitting alone on bench eating sandwich looking melancholy, lonely celebrity", "https://i.imgflip.com/baq37.jpg", "emotion"),
    ("Success Kid", "toddler clenching fist in triumph with sand on face, small victory celebration", "https://i.imgflip.com/1bhk.jpg", "emotion"),
    ("Bad Luck Brian", "awkward school photo with sweater vest braces, everything goes wrong", "https://i.imgflip.com/1bip.jpg", "emotion"),
    ("Overly Attached Girlfriend", "woman with intense staring wide eyes obsessive gaze, clingy possessive", "https://i.imgflip.com/1biq.jpg", "emotion"),
    ("Futurama Fry Not Sure", "man squinting eyes suspiciously, not sure if genuine or sarcasm", "https://i.imgflip.com/1bgw.jpg", "emotion"),
    ("Y U No", "angry stick figure demanding why you no do thing, frustrated expectation", "https://i.imgflip.com/1bh1.jpg", "emotion"),
    ("Forever Alone", "simple drawn face crying alone, perpetual loneliness no friends", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Feels Good Man", "green frog smiling contentedly, satisfaction pleasure pepe the frog happy", "https://i.imgflip.com/yj5nj.jpg", "emotion"),
    ("Rage Face", "extremely angry red faced screaming stick figure, uncontrollable fury", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Stonks", "businessman in front of rising stock graph, financial success winning", "https://i.imgflip.com/3s7dmi.jpg", "emotion"),
    ("Not Stonks", "businessman in front of falling stock graph, financial failure losing", "https://i.imgflip.com/3s7dmi.jpg", "emotion"),
    ("Pain", "man clutching chest in agony pain face, emotional damage suffering", "https://i.imgflip.com/5c7lwq.jpg", "emotion"),
    ("Emotional Damage", "asian man declaring emotional damage, devastating verbal blow", "https://i.imgflip.com/62fen1.jpg", "emotion"),
    ("Crying Jordan", "basketball legend with tears photoshopped onto face, losing sadness failure", "https://i.imgflip.com/15cphl.jpg", "emotion"),
    ("Shocked Pikachu Face", "electric mouse with jaw dropped wide open mouth, stunned shocked reaction", "https://i.imgflip.com/2kbn1e.jpg", "emotion"),
    ("Visible Confusion", "person with extremely confused puzzled face question marks, bewilderment", "https://i.imgflip.com/2k0qad.jpg", "emotion"),
    ("Anxiety Cat", "cat with extremely wide nervous eyes, anxious paranoid worried", "https://i.imgflip.com/1alsi2.jpg", "emotion"),
    ("Inner Peace", "kung fu panda finding inner peace serenity calm, zen meditation", "https://i.imgflip.com/3igo2m.jpg", "emotion"),
    ("Happiness Noise", "dog making happy satisfied face sound, pure joy contentment", "https://i.imgflip.com/3f82s3.jpg", "emotion"),

    # ── NATURE & OUTDOOR SPECIFIC ─────────────────────────────────────────────
    ("Touch Grass", "hand reaching down to touch green grass, go outside digital detox", "https://i.imgflip.com/5vpj1e.jpg", "nature"),
    ("Tree Fiddy", "loch ness monster asking for tree fiddy three fifty, unexpected request creature", "https://i.imgflip.com/6ila.jpg", "nature"),
    ("Bob Ross Happy Little Trees", "painter creating happy little trees no mistakes accidents, wholesome art", "https://i.imgflip.com/18gx76.jpg", "nature"),
    ("Bear Grylls", "survival expert drinking own urine in wilderness, extreme measures", "https://i.imgflip.com/1bgs.jpg", "nature"),
    ("Rock Eyebrow Raise", "muscular man raising one eyebrow suspiciously, skeptical rock face", "https://i.imgflip.com/5r32ot.jpg", "nature"),
    ("Pepe Rain", "sad frog sitting in rain getting wet, melancholy outdoor moment", "https://i.imgflip.com/1gs0ix.jpg", "nature"),
    ("Cloud That Looks Like Something", "cloud formation resembling face or object in sky, pareidolia", "https://i.imgflip.com/3igo2m.jpg", "nature"),
    ("Flower Power", "person giving flower to armored soldier, peace vs violence nature", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Into The Wild", "man walking alone into vast wilderness adventure, freedom exploration", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Nature Is Healing", "beautiful natural scene returning during lockdown, the planet recovering", "https://i.imgflip.com/3xo7w1.jpg", "nature"),
    ("Butterfly Effect", "tiny butterfly causing hurricane across world, small change big consequence", "https://i.imgflip.com/1o00in.jpg", "nature"),
    ("Mountain Goat", "goat standing impossibly on cliff face defying gravity, determination balance", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Sunset Aesthetic", "beautiful gradient sky at golden hour warm colors, vaporwave aesthetic sunrise", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Foggy Mystery", "thick fog obscuring landscape mysterious atmosphere eerie silent hill vibes", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Perfect Puddle Reflection", "puddle on ground perfectly reflecting sky above, mirror dimension portal", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Mushroom Wisdom", "fungus growing wise old mushroom sage forest floor, mycelium intelligence", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Dramatic Squirrel", "squirrel turning dramatically like chipmunk cousin, startled wildlife moment", "https://i.imgflip.com/9vct.jpg", "nature"),
    ("Bird Stare", "bird looking directly at camera intensely, judgemental avian gaze", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Leaf On The Wind", "single leaf floating gracefully in breeze, serene peaceful drift", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Moss Cathedral", "ancient tree covered in moss in old growth forest, sacred natural temple", "https://i.imgflip.com/1bij.jpg", "nature"),

    # ── PAREIDOLIA SPECIFIC (faces in objects) ────────────────────────────────
    ("Face In Tree", "tree bark forming human face with eyes nose mouth, pareidolia wood spirit", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Angry Electrical Outlet", "wall outlet looking like surprised or angry face, two eyes open mouth", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Happy Building", "building facade windows forming smiley face, architectural pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Sad Bag", "plastic bag looking sad droopy face, melancholy trash pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Rock Face", "rock formation looking like human profile face, natural sculpture geology", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Moon Face", "moon surface showing face features the man in the moon, celestial pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Car Face", "car front headlights and grill forming face expression, vehicle personality", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Cloud Face", "cloud formation clearly showing human face features, sky pareidolia atmospheric", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Manhole Smile", "manhole cover pattern looking like smiley face, urban pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Knot Eye", "tree knot looking like single eye watching, wood spirit surveillance", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Pepper Scream", "cut bell pepper showing screaming face like edvard munch, vegetable horror", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Bin Monster", "trash bin lid looking like monster mouth with teeth, waste creature", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Fence Watcher", "fence posts spacing creating face pattern, suburban pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Stone Guardian", "stone wall arrangement forming face guardian watching, ancient protection", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Puddle Portal", "water puddle reflecting in way that creates face or portal, liquid pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Crack Smile", "crack in pavement forming smile curve, happy concrete", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Window Surprise", "windows and door forming surprised face, building expression", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Rust Portrait", "rust patterns on metal forming face or figure, oxidation art", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Root Creature", "tree roots forming creature or dragon shape, organic sculpture", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Bark Beast", "tree bark texture resembling monster or beast face, forest creature", "https://i.imgflip.com/1bij.jpg", "pareidolia"),

    # ── CLASSIC TEMPLATES ─────────────────────────────────────────────────────
    ("Ancient Aliens", "man with wild hair saying aliens, everything explained by extraterrestrials", "https://i.imgflip.com/26am.jpg", "classic"),
    ("X X Everywhere", "buzz lightyear showing woody infinite expanse, pointing at abundance", "https://i.imgflip.com/1ihzfe.jpg", "classic"),
    ("All The Things", "stick figure aggressively doing all the things with broom, hyperactive", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Philosoraptor", "thinking dinosaur pondering deep questions, philosophical velociraptor wisdom", "https://i.imgflip.com/1bgx.jpg", "classic"),
    ("Scumbag Steve", "man in tilted hat being inconsiderate, selfish rude behavior", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Good Guy Greg", "friendly smiling man being helpful and kind, wholesome altruism", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Socially Awkward Penguin", "penguin in awkward social situation, cringe embarrassment", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Conspiracy Keanu", "keanu reeves looking shocked at conspiracy theory realization, mind blown", "https://i.imgflip.com/3po4m7.jpg", "classic"),
    ("Keep Calm", "british wartime poster keep calm and carry on, stoic persistence", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Captain America Understood", "superhero saying I understood that reference, pop culture recognition", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Boromir", "warrior saying one does not simply walk into mordor, difficulty warning", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Morpheus", "man in sunglasses offering red and blue pill truth, matrix choice", "https://i.imgflip.com/z6fq.jpg", "classic"),
    ("Yoda Advice", "small green wise alien giving sage advice, backward syntax wisdom", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Batman Slap", "superhero slapping sidekick for saying something stupid, shut up correction", "https://i.imgflip.com/9ehk.jpg", "classic"),
    ("Grandma Computer", "elderly woman confused at computer screen, technology bewilderment", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Third World Skeptical Kid", "african child looking skeptical at camera, disbelief questioning", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Condescending Wonka", "willy wonka leaning forward with sarcastic smile, patronizing tell me more", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Laughing Leo", "leonardo dicaprio laughing with glass in hand, finding something hilarious", "https://i.imgflip.com/26jxvz.jpg", "classic"),
    ("Facepalm", "person covering face with palm in disappointment, exasperation stupidity", "https://i.imgflip.com/1bij.jpg", "classic"),
    ("Deal With It", "putting on sunglasses coolly, unbothered confident acceptance", "https://i.imgflip.com/1bij.jpg", "classic"),

    # ── MODERN/GEN-Z MEMES ────────────────────────────────────────────────────
    ("Among Us Suspicious", "colored astronaut being accused of being imposter, sus suspicious trust issues", "https://i.imgflip.com/4jvhka.jpg", "modern"),
    ("Amogus", "everything looking like among us character shape, cannot unsee everywhere", "https://i.imgflip.com/5c7lwq.jpg", "modern"),
    ("Sigma Male", "lone wolf grinding alone on sigma grindset, independent hustle stoic", "https://i.imgflip.com/5fcnzj.jpg", "modern"),
    ("Its Free Real Estate", "man whispering about free real estate opportunity, cant pass this up", "https://i.imgflip.com/2b3n5k.jpg", "modern"),
    ("Fernanfloo Laughing", "latino youtuber laughing uncontrollably at something hilarious", "https://i.imgflip.com/3oevdk.jpg", "modern"),
    ("Shaq Hot Wings", "basketball giant eating extremely hot wing sweating, spicy food challenge", "https://i.imgflip.com/3kwx2c.jpg", "modern"),
    ("This Is Brilliant But I Like This", "man preferring simple crude thing over elegant solution", "https://i.imgflip.com/2ga1hf.jpg", "modern"),
    ("Coffin Dance", "african pallbearers dancing with coffin astronomia, celebrating death meme", "https://i.imgflip.com/3tp5xs.jpg", "modern"),
    ("Vibe Check", "floating entity approaching with glowing fist for vibe assessment, approval test", "https://i.imgflip.com/3k3epj.jpg", "modern"),
    ("Ight Imma Head Out", "sponge character getting up and leaving, done with this situation", "https://i.imgflip.com/3afmhv.jpg", "modern"),
    ("Weakest Fan vs Average Enjoyer", "crying anime fan vs smiling gigachad enjoyer, sophisticated preference", "https://i.imgflip.com/5bx4t9.jpg", "modern"),
    ("Drakeposting", "rapper rejecting first option embracing second, preference template", "https://i.imgflip.com/30b1gx.jpg", "modern"),
    ("Soyboy Pointing", "excited man pointing at something enthusiastically, overreaction amazement", "https://i.imgflip.com/5fcnzj.jpg", "modern"),
    ("Living In Spain Without S", "person suffering in pain wordplay, spain without the s equals pain", "https://i.imgflip.com/4ecbya.jpg", "modern"),
    ("Trollface", "classic drawn face with mischievous grin, problem troll u mad", "https://i.imgflip.com/1bij.jpg", "modern"),
    ("Pepe Sad", "sad green frog crying tears, feels bad man depression", "https://i.imgflip.com/1gs0ix.jpg", "modern"),
    ("Pepe Happy", "happy green frog smiling wide, feels good man joy", "https://i.imgflip.com/yj5nj.jpg", "modern"),
    ("Pepe Angry", "angry red green frog seething with rage, reeee furious", "https://i.imgflip.com/1bij.jpg", "modern"),
    ("Wojak Nordic", "blonde nordic gigachad saying yes to everything, agreeable powerful", "https://i.imgflip.com/5dnv1l.jpg", "modern"),
    ("NPC Wojak", "grey emotionless face with empty expression, hive mind no independent thought", "https://i.imgflip.com/2wifhj.jpg", "modern"),

    # ── SHAPES & TEXTURES (for pareidolia matching) ───────────────────────────
    ("Round Face", "perfectly circular round shape resembling face, moon ball sphere", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Triangle Illuminati", "triangle shape with eye, illuminati confirmed all seeing pyramid", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Spiral Hypnotic", "spiral pattern hypnotic swirling mesmerizing, vortex tunnel optical illusion", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Heart Shape Natural", "natural heart shape found in nature, love romantic accidental heart", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Star Pattern", "star shape found naturally, celebrity five pointed pentagram", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Fractal Nature", "natural fractal pattern in broccoli fern frost, mathematical beauty recursive", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Symmetry Perfect", "perfectly symmetrical natural formation, balanced mirror image satisfying", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Crack Lightning", "crack pattern resembling lightning bolt, energy power electric natural", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Wave Pattern", "natural wave pattern in sand water wood, flowing rhythm organic", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Dot Matrix", "pattern of dots forming image from distance, pointillism natural pixels", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Straight Lines", "unnaturally straight line in nature, glitch in matrix simulation theory", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Golden Ratio", "fibonacci spiral golden ratio in nature, mathematical perfection shell", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Tessellation", "repeating interlocking pattern tiles, escher like mathematical art", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Shadow Art", "shadow cast creating recognizable figure or face, light sculpture accidental", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Reflection Symmetry", "reflection in water creating perfect mirror, upside down world", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Organic Curves", "smooth curved natural form sensual organic flowing, art nouveau nature", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Rough Texture", "rough jagged aggressive texture, brutal raw savage surface", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Smooth Gradient", "smooth color gradient transition in nature, sunrise sky ombre", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Layered Strata", "visible geological layers stratification, time history earth cake", "https://i.imgflip.com/1bij.jpg", "shape"),
    ("Radial Burst", "rays emanating from center point sunburst, explosion energy radiating", "https://i.imgflip.com/1bij.jpg", "shape"),

    # ── EXPANDED REACTION SET (more coverage) ─────────────────────────────────
    ("Evil Kermit", "frog talking to hooded evil version of self, dark temptation inner demon", "https://i.imgflip.com/1e0rkr.jpg", "reaction"),
    ("Kermit Tea", "frog sipping tea minding own business, but thats none of my business", "https://i.imgflip.com/19mid.jpg", "reaction"),
    ("Salt Bae", "chef sprinkling salt elegantly from fingertips, seasoning perfection flair", "https://i.imgflip.com/1k5vza.jpg", "reaction"),
    ("Galaxy Brain", "ascended transcendent intelligence cosmic brain, ultimate understanding", "https://i.imgflip.com/4a0vsi.jpg", "reaction"),
    ("Surprised Chris Pratt", "actor looking genuinely surprised mouth open, amazement shock", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Jim Halpert Whiteboard", "office worker presenting on whiteboard facts, logical explanation", "https://i.imgflip.com/3f82s3.jpg", "reaction"),
    ("Think Mark Think", "superhero standing over beaten hero demanding answers, aggressive questioning", "https://i.imgflip.com/5bx4t9.jpg", "reaction"),
    ("They Called Me A Madman", "purple titan vindicated, they said I was crazy but I was right", "https://i.imgflip.com/2r6u8z.jpg", "reaction"),
    ("Anakin Padme Meme", "star wars couple where she realizes his true intentions, ominous revelation", "https://i.imgflip.com/5c7lwq.jpg", "reaction"),
    ("Fine Ill Do It Myself", "villain frustrated putting on gauntlet, taking matters into own hands", "https://i.imgflip.com/28j0te.jpg", "reaction"),
    ("Wait A Minute", "person suddenly realizing something important, delayed comprehension", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Understandable Have A Great Day", "accepting response to bizarre situation, polite exit", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Outstanding Move", "chess genius making brilliant unexpected move, galaxy brain strategy", "https://i.imgflip.com/2wifhj.jpg", "reaction"),
    ("Modern Problems Modern Solutions", "man tapping head with clever solution, innovative thinking", "https://i.imgflip.com/1h7in3.jpg", "reaction"),
    ("Perfection", "man looking at something beautiful with tears of joy, pure appreciation", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Not Bad Obama", "former president nodding in approval with impressed face, decent acceptable", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Confused Math Lady", "woman surrounded by floating math equations, complex calculation overwhelm", "https://i.imgflip.com/2k0qad.jpg", "reaction"),
    ("My Goals Are Beyond Your Understanding", "villain explaining incomprehensible master plan, advanced thinking", "https://i.imgflip.com/3k3epj.jpg", "reaction"),
    ("Perhaps", "cow looking thoughtfully perhaps considering, maybe contemplation", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Noted", "penguin writing down notes, acknowledged recorded information", "https://i.imgflip.com/4k0l2q.jpg", "reaction"),

    # ── OUTDOOR ACTIVITIES & SPORTS ───────────────────────────────────────────
    ("Running Man", "person running urgently from something, escape flee sprint", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Planking", "person lying flat face down on random surface, planking trend", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Dabbing", "person doing dab dance move arm over face, celebration", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Parkour Office", "person doing parkour over obstacles, hardcore free running", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Walking Away From Explosion", "cool person walking away from explosion without looking, badass", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Bike Fall", "person putting stick in own bike wheel and falling, self sabotage", "https://i.imgflip.com/1b42wl.jpg", "activity"),
    ("Skateboard Trick Fail", "attempted trick on skateboard going wrong, bail fail", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Yoga Pose Nature", "person doing yoga in scenic outdoor location, mindfulness wellness", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Fishing For Answers", "person patiently fishing waiting for catch, patience persistence", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Bird Watching", "person with binoculars looking at birds, nerd hobby observation", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Camping Disaster", "tent collapsed or campfire out of control, outdoor fail", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Hiking Summit", "person standing triumphantly on mountain peak, achievement conquered", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Picnic Ants", "ants invading picnic stealing food, nature fights back", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Dog Walking", "person being dragged by enthusiastic dog on leash, who walks whom", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Garden Gnome", "garden gnome statue guarding yard, silent sentinel protector", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Lawn Mowing", "perfectly mowed lawn with satisfying lines, precision satisfaction", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Puddle Jump", "person or child jumping into puddle with splash, childlike joy", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Slipping On Ice", "person about to slip on icy surface, winter danger", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Sunburn Regret", "person with terrible sunburn lines, outdoor consequence", "https://i.imgflip.com/1bij.jpg", "activity"),
    ("Getting Lost", "person confused looking at map or phone outdoors, navigation fail", "https://i.imgflip.com/1bij.jpg", "activity"),

    # ── INTERNET CULTURE / VIRAL ──────────────────────────────────────────────
    ("Rickroll", "man dancing in music video never gonna give you up, tricked link", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Gangnam Style", "korean pop star doing horse riding dance, psy viral dance", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Harlem Shake", "office suddenly erupting into chaotic dance, viral dance trend", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Double Rainbow", "man ecstatically recording double rainbow in sky, overwhelming beauty awe", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Charlie Bit My Finger", "baby biting older brothers finger, sibling pain comedy", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Sneezing Panda", "baby panda sneezing startling mother panda, cute surprise", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Keyboard Cat", "cat playing keyboard wearing shirt, musical feline performer", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Leroy Jenkins", "man running into battle yelling own name, reckless charge", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("OK Boomer", "dismissive response to older generation, generational divide snark", "https://i.imgflip.com/3e0e3.jpg", "viral"),
    ("Harambe", "beloved gorilla memorial, never forget tribute justice", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Loss", "four panel minimalist comic about loss, | || || |_ deep meaning", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Distortion", "deep fried overly saturated distorted image, chaotic energy", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Surreal Meme", "absurdist meme with floating objects and void, meaningless profound", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("E", "lord farquaad markiplier merged face saying E, pure absurdity", "https://i.imgflip.com/2dpklu.jpg", "viral"),
    ("Yeet", "forcefully throwing object or person away, extreme launch", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Bruh", "deadpan reaction of disbelief, bruh moment certification", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Sheesh", "teeth sucking appreciation sound, impressive reaction", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("No Cap", "speaking truthfully without exaggeration, blue cap emoji honest", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Bussin", "food or thing being extraordinarily good, fire excellent chef", "https://i.imgflip.com/1bij.jpg", "viral"),
    ("Ratio", "getting more likes than original post, social media dominance", "https://i.imgflip.com/1bij.jpg", "viral"),

    # ── STREET & URBAN PAREIDOLIA ─────────────────────────────────────────────
    ("Mailbox Monster", "mailbox looking like monster with open mouth, suburban creature", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Traffic Light Face", "traffic light arrangement forming face, urban signal pareidolia", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Hydrant Hero", "fire hydrant looking like short stocky hero character, street guardian", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Bench Philosopher", "park bench looking contemplative or wise, urban furniture wisdom", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Pothole Portal", "deep pothole looking like portal to another dimension, road damage mystical", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Graffiti Ghost", "graffiti or street art looking like ghost figure, urban phantom", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Manhole Mandala", "manhole cover pattern intricate circular design, urban sacred geometry", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Pipe Organ", "exposed pipes on building resembling organ instrument, urban music", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Street Sign Wisdom", "street sign text forming philosophical statement, accidental poetry", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Bollard Army", "row of bollards looking like army of short soldiers, urban defense force", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Drain Scream", "drainage grate looking like screaming mouth, storm drain horror", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Lamppost Lean", "leaning lamppost looking like tired person, exhausted illumination", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Stairway Pattern", "staircase creating geometric pattern from above, urban geometry", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Wall Crack Map", "cracked wall pattern resembling map or country borders, geological wall", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Window Eyes", "two windows looking like pair of eyes watching, building surveillance", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Door Mouth", "door with handle and mail slot forming face, entrance expression", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Cone Wizard", "traffic cone looking like wizard hat on ground, road magic", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Puddle Galaxy", "oil puddle with rainbow swirl resembling galaxy, microscopic universe", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Bike Rack Antlers", "bike rack looking like antlers or horns, urban deer", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Sidewalk Crack River", "crack in sidewalk looking like river delta from above, concrete geography", "https://i.imgflip.com/1bij.jpg", "urban"),

    # ── FOOD & OBJECTS PAREIDOLIA ─────────────────────────────────────────────
    ("Toast Jesus", "burnt toast pattern resembling face of jesus, breakfast miracle", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Banana Smile", "banana curve naturally forming smiley face, happy fruit", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Pretzel Arms", "pretzel looking like crossed arms or figure, bakery body language", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Tomato Anger", "tomato with wrinkle pattern looking angry, furious fruit", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Potato Wisdom", "potato with markings resembling wise old face, tuber sage", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Latte Art Face", "coffee foam art accidentally forming face, caffeinated portrait", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Burnt Food Art", "burnt food forming recognizable shape or face, culinary disaster art", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Bottle Judgement", "bottle arrangement looking like judging face, container criticism", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Fork Road", "fork in literal road vs eating utensil, visual pun wordplay", "https://i.imgflip.com/1bij.jpg", "food"),
    ("Spoon Reflection", "spoon reflecting upside down face, distorted self portrait", "https://i.imgflip.com/1bij.jpg", "food"),

    # ── WEATHER & SKY ─────────────────────────────────────────────────────────
    ("Angry Cloud", "storm cloud formation looking angry threatening, weather rage", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Happy Sun Face", "sun with face drawn or seen through haze, cheerful celestial", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Lightning Dragon", "lightning bolt pattern resembling dragon or creature, electric beast", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Rainbow End", "rainbow ending at specific spot, treasure location promise", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Fog Monster", "fog bank rolling in looking like creature approaching, atmospheric horror", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Wind Direction", "trees all bent one direction from prevailing wind, nature pointing", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Snow Sculpture", "natural snow formation looking like figure or face, winter art", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Ice Crystal Face", "frost pattern on window forming face or figure, frozen portrait", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Cloud Animal", "cloud shaped exactly like specific animal, sky zoo", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Sunset Silhouette", "sunset creating dramatic silhouette that resembles figure, golden hour shadow", "https://i.imgflip.com/1bij.jpg", "weather"),

    # ── ARCHITECTURE PAREIDOLIA ───────────────────────────────────────────────
    ("Building Face", "building facade forming clear face expression, architectural emotion", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Roof Eyebrows", "roof line looking like raised eyebrows, surprised house", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Chimney Hat", "chimney looking like top hat on building, dapper house", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Garage Mouth", "garage door forming mouth of building, hungry house", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Tower Guardian", "tower or spire looking like standing guard, architectural sentinel", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Bridge Smile", "bridge arch forming smile curve, happy crossing", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Fence Teeth", "fence pickets looking like row of teeth, grinning barrier", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Balcony Eyes", "balcony railings forming eye shapes, watching building", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Arch Surprise", "archway forming O shape of surprise, architectural gasp", "https://i.imgflip.com/1bij.jpg", "architecture"),
    ("Column March", "row of columns looking like marching figures, architectural procession", "https://i.imgflip.com/1bij.jpg", "architecture"),

    # ── TEXTURE MATCHES (for outdoor surface detection) ───────────────────────
    ("Cracked Earth", "dry cracked earth mud pattern, drought desert desolation", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Moss Carpet", "thick green moss covering surface, soft natural carpet verdant", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Lichen Pattern", "colorful lichen growing on rock, organism colony artwork", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Bark Ridges", "deep ridged tree bark texture, ancient rough protective", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Pebble Mosaic", "natural arrangement of smooth pebbles, river stone art", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Sand Ripple", "wind created ripple pattern in sand, desert waves texture", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Water Sparkle", "sunlight sparkling on water surface, diamond light liquid", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Leaf Vein", "intricate vein pattern on leaf backlit, biological network map", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Cobweb Geometry", "spider web with dew drops, natural engineering precision", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Rust Patina", "beautiful rust oxidation pattern on metal, decay art time", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Peeling Paint", "paint peeling off surface revealing layers beneath, decay archaeology", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Worn Stone", "stone worn smooth by years of contact, erosion time patience", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Wood Grain", "beautiful wood grain swirling pattern, natural abstract art growth rings", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Crystal Formation", "natural crystal or mineral formation, geological treasure sparkle", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Coral Pattern", "coral or organic branching pattern, underwater tree fractal", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Honeycomb", "hexagonal honeycomb pattern natural or artificial, perfect geometry efficiency", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Bubble Cluster", "cluster of bubbles with light refraction, foam sphere grouping", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Woven Texture", "interlocking woven pattern basket or textile, craftsmanship tradition", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Concrete Aggregate", "exposed aggregate concrete surface, urban mineral composite", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Marble Vein", "natural marble veining pattern, luxury stone organic lines", "https://i.imgflip.com/1bij.jpg", "texture"),

    # ── EXPANDED MEME CATEGORIES (filling toward 1500) ────────────────────────

    # More reaction faces
    ("Shut Up And Take My Money", "man offering money aggressively, immediate purchase desire", "https://i.imgflip.com/3si4.jpg", "reaction"),
    ("Grandma Finds Internet", "grandmother discovering internet for first time, amazed confused", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("One Does Not Simply Meme", "cannot simply do the thing without consequences, warning complexity", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Wait Thats Illegal", "pointing out something should not be allowed, rule violation", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Professionals Have Standards", "sniper explaining professional ethics, surprisingly principled", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Task Failed Successfully", "windows error saying task failed successfully, paradoxical success", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Unlimited Power", "emperor cackling with electricity, absolute authority dark side", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("Hello There", "jedi master greeting casually before fight, iconic entrance", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("A Surprise To Be Sure", "a surprise to be sure but a welcome one, pleasant unexpected", "https://i.imgflip.com/1bij.jpg", "reaction"),
    ("You Have No Power Here", "wizard declaring opponents powerlessness, authority dominance", "https://i.imgflip.com/1bij.jpg", "reaction"),

    # More nature/outdoor concepts
    ("Tiny Flower In Crack", "small flower growing through concrete crack, resilience persistence hope", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Spider Web Morning Dew", "spider web with morning dew drops glistening, nature jewelry precision", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Fallen Log Bridge", "fallen tree creating natural bridge over stream, nature engineering", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Ant Trail Highway", "line of ants marching carrying food, organized labor nature logistics", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Bird Formation V", "birds flying in V formation across sky, teamwork aerodynamics migration", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Caterpillar Journey", "caterpillar slowly crossing path, slow progress determination metamorphosis", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Dandelion Wish", "dandelion seeds blowing in wind, wishes dreams scattering hope", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Pinecone Fibonacci", "pinecone showing fibonacci spiral pattern, mathematical nature perfection", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Frog Contemplation", "frog sitting still on lily pad or rock, amphibian meditation zen", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Snail Trail", "snail leaving silvery trail on surface, slow progress visible path", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Mushroom Circle", "fairy ring of mushrooms in circle, magical woodland mystery", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Twisted Tree", "dramatically twisted or bent tree, wind shaped persistence character", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Root System Exposed", "tree root system exposed showing network, underground internet of trees", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Icicle Teeth", "row of icicles hanging from roof like teeth, winter smile frozen grin", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Autumn Leaf Color", "single perfect autumn leaf in vibrant red or gold, seasonal beauty change", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Puddle World", "upside down world reflected in still puddle, alternate dimension mirror", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Moss Writing", "moss growing in pattern resembling letters or words, nature message", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Bird Nest Architecture", "intricately woven bird nest engineering marvel, avian construction", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Wildflower Meadow", "field of colorful wildflowers stretching to horizon, natural garden", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Tide Pool World", "tide pool with tiny ecosystem, miniature ocean world contained", "https://i.imgflip.com/1bij.jpg", "nature"),

    # Pop culture / movie references
    ("This Is Sparta", "warrior kicking enemy into pit, dramatic rejection force", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("I Am Inevitable", "villain declaring their inevitability, unstoppable force destiny", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("You Shall Not Pass", "wizard blocking bridge with staff, denial protection stand", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("I Am Your Father", "villain revealing paternal relationship to hero, shocking revelation", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("Houston We Have A Problem", "astronaut reporting problem calmly, understatement crisis", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("Ill Be Back", "cyborg promising to return, ominous commitment determination", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("Run Forrest Run", "man running across country fields, unstoppable momentum", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("Here's Johnny", "axe through door menacing face, horror breakthrough invasion", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("May The Force", "using the force telekinetic hand gesture, mystical power space religion", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("ET Phone Home", "alien with glowing finger pointing to sky, homesick communication", "https://i.imgflip.com/1bij.jpg", "movie"),

    # More urban/street scene matches
    ("Street Art Banksy Style", "satirical street art commentary on society, guerrilla art activism", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Broken Clock Right", "broken clock still right twice a day, accidental accuracy", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Vending Machine Tilt", "vending machine with item stuck, frustration capitalism struggle", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Crosswalk Art", "creative crosswalk painting or modification, pedestrian art", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Bench Memorial", "park bench with memorial plaque, remembered legacy quiet tribute", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Broken Fence Escape", "gap in broken fence like escape route, freedom portal", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Shadow Play", "interesting shadow cast by object creating new image, light art", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Peeling Poster Layers", "layers of old posters peeling revealing history beneath, temporal archaeology", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Emergency Stairs Spiral", "spiral emergency staircase dizzying geometry, urban vertigo", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Abandoned Cart", "shopping cart abandoned in random location, urban tumbleweed migration", "https://i.imgflip.com/1bij.jpg", "urban"),

    # More emotional/relatable templates
    ("Monday Morning", "person exhausted and miserable on monday morning, weekly dread cycle", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Friday Feeling", "ecstatic celebration because its friday, weekend anticipation liberation", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Introvert Energy", "hiding from social interaction, recharging alone preferred solitude", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Procrastination", "doing everything except the one important task, avoidance productivity", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Comfort Zone", "staying inside safe comfort zone bubble, refusing adventure growth", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Nostalgia", "remembering old times with bittersweet fondness, past glory memory", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Decision Paralysis", "unable to choose from too many options, overwhelmed choices frozen", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Imposter Syndrome", "feeling like fraud despite achievements, self doubt deception anxiety", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("Main Character Energy", "walking through life like protagonist of movie, confidence narrative", "https://i.imgflip.com/1bij.jpg", "emotion"),
    ("NPC Energy", "going through motions without awareness, background character automation", "https://i.imgflip.com/1bij.jpg", "emotion"),

    # Gaming references
    ("Its Dangerous To Go Alone", "take this sword offered by old man in cave, helpful stranger", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Press F To Pay Respects", "pressing F key to pay respects, memorial button funeral", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("GG", "good game said at end of match, sportsmanship acknowledgement", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Speedrun", "completing task as fast as absolutely possible, optimization efficiency", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Side Quest", "getting distracted from main objective by side task, ADHD adventure", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Boss Music", "intense music starting playing indicating boss fight incoming, danger escalation", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Loading Screen Tips", "obvious useless advice during loading, unhelpful wisdom patronizing", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Respawn Point", "returning to checkpoint after failure, second chance retry", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Minecraft Creeper", "green blocky creature about to explode behind player, surprise destruction", "https://i.imgflip.com/1bij.jpg", "gaming"),
    ("Achievement Unlocked", "gaming achievement popup notification, milestone reached rewarded", "https://i.imgflip.com/1bij.jpg", "gaming"),

    # More expanded categories to reach ~500+ unique
    ("Butterfly Knife", "butterfly knife trick impressive, skills dexterity dangerous talent", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Rubber Duck Debug", "explaining code to rubber duck debugging method, talking to toy solves problems", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Traffic Jam Zen", "stuck in traffic accepting fate calmly, urban meditation patience", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Umbrella Wind", "umbrella inverted by strong wind, weather defeat surrender", "https://i.imgflip.com/1bij.jpg", "weather"),
    ("Paper Airplane", "paper airplane soaring through air, simple engineering flight dreams", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Bubble Pop", "soap bubble about to pop with swirling rainbow colors, fragile beauty temporary", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Key In Lock", "key about to turn in lock, access permission breakthrough moment", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Mirror Reflection", "unexpected reflection in mirror or surface, double self confrontation", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Clock Hands Alignment", "clock hands perfectly aligned, timing synchronicity moment", "https://i.imgflip.com/1bij.jpg", "object"),
    ("Slinky Stairs", "slinky toy walking down stairs, satisfying physics gravity rhythm", "https://i.imgflip.com/1bij.jpg", "object"),

    # Visual puns and wordplay memes
    ("Literal Eyebrow Raising", "physical eyebrow shape found in nature, literal interpretation", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Actual Diamond Hands", "diamond shaped rock formation resembling hand, geological investment joke", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Real Snake In Grass", "actual snake in grass discovering, literal phrase materialized", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Touching Actual Grass", "hand literally touching grass blade, digital detox touchgrass movement", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Leaf Me Alone", "pile of leaves covering person, autumn wordplay hiding nature", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Rock And Roll", "rock literally rolling down hill, geological music pun", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Flower Power Outlet", "flower growing from power outlet shaped crack, energy nature fusion", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Branch Manager", "stick or branch resting on bench like manager, nature office humor", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Current Events", "river current flowing creating pattern, water news pun nature", "https://i.imgflip.com/1bij.jpg", "wordplay"),
    ("Ground Breaking", "ground literally breaking apart cracking, construction earth humor", "https://i.imgflip.com/1bij.jpg", "wordplay"),

    # Additional memes to round out the collection
    ("Thanos Did Nothing Wrong", "villain was right all along balanced universe, controversial agreement", "https://i.imgflip.com/28j0te.jpg", "movie"),
    ("We Live In A Society", "joker reflecting on society, deep philosophical commentary clown", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("Reality Is Often Disappointing", "villain lamenting reality falls short of expectations", "https://i.imgflip.com/2r6u8z.jpg", "movie"),
    ("Impossible Mission", "secret agent receiving impossible mission, challenge accepted dangerous", "https://i.imgflip.com/1bij.jpg", "movie"),
    ("To Infinity And Beyond", "space ranger declaring limitless potential, unlimited ambition", "https://i.imgflip.com/1bij.jpg", "movie"),

    # Even more variety
    ("Flex Tape", "man applying flex tape to fix massive leak, extreme repair solution", "https://i.imgflip.com/1bij.jpg", "modern"),
    ("Elmo Rise", "elmo puppet rising with fire behind, chaotic energy destruction", "https://i.imgflip.com/1bij.jpg", "modern"),
    ("Math Is Math", "frustrated man insisting math is math, obvious truth resistance", "https://i.imgflip.com/3f82s3.jpg", "modern"),
    ("Confused Screaming", "person screaming in confusion, overwhelmed panicking chaotic", "https://i.imgflip.com/1bij.jpg", "modern"),
    ("Signature Look Of Superiority", "looking down with smug superiority, condescending dominance", "https://i.imgflip.com/1bij.jpg", "modern"),
    ("Mother Nature", "personification of nature as powerful woman, earth spirit ecosystem guardian", "https://i.imgflip.com/1bij.jpg", "nature"),
    ("Concrete Jungle", "urban landscape as jungle metaphor, city wilderness glass steel forest", "https://i.imgflip.com/1bij.jpg", "urban"),
    ("Hidden Mickey", "three circles forming hidden mickey mouse shape, disney pareidolia", "https://i.imgflip.com/1bij.jpg", "pareidolia"),
    ("Texture Abstract", "close up texture becoming abstract art, macro microscopic beauty", "https://i.imgflip.com/1bij.jpg", "texture"),
    ("Color Palette Nature", "natural color combination forming perfect palette, design inspiration", "https://i.imgflip.com/1bij.jpg", "nature"),
]


async def seed_memes():
    """Main seeding function: compute embeddings and upsert to MongoDB Atlas."""
    settings = get_settings()

    print(f"[Seed] 🌿 Grasschalant Meme Vault Seeder")
    print(f"[Seed] Database: {settings.MONGODB_DB_NAME}")
    print(f"[Seed] Collection: {settings.MONGODB_COLLECTION_MEMES}")
    print(f"[Seed] Total archetypes: {len(MEME_ARCHETYPES)}")

    # 1. Prepare description texts for batch embedding
    print("[Seed] 📐 Computing CLIP embeddings (this may take a moment)...")
    descriptions = [desc for _, desc, _, _ in MEME_ARCHETYPES]
    embeddings = embed_texts_batch(descriptions)
    print(f"[Seed] ✅ Generated {len(embeddings)} embeddings (dim={len(embeddings[0])})")

    # 2. Build documents
    documents = []
    for i, (name, description, image_url, category) in enumerate(MEME_ARCHETYPES):
        # Extract visual tags from description
        tags = [t.strip() for t in description.replace(",", " ").split() if len(t.strip()) > 2][:10]

        documents.append({
            "name": name,
            "description": description,
            "visual_tags": tags,
            "image_url": image_url,
            "category": category,
            "embedding": embeddings[i],
        })

    # 3. Connect and upsert
    print("[Seed] 🔗 Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    collection = db[settings.MONGODB_COLLECTION_MEMES]

    # Drop existing and re-insert for clean state
    await collection.drop()
    print("[Seed] 🗑️  Cleared existing meme_vault collection")

    # Batch insert
    result = await collection.insert_many(documents)
    print(f"[Seed] ✅ Inserted {len(result.inserted_ids)} meme archetypes into meme_vault")

    # 4. Create standard index on name for lookups
    await collection.create_index("name", unique=True)
    await collection.create_index("category")
    print("[Seed] 📇 Created standard indexes on name and category")

    print()
    print("[Seed] ⚠️  IMPORTANT: You must manually create the Atlas Vector Search index!")
    print("[Seed] Go to MongoDB Atlas > Database > Browse Collections > Search Indexes")
    print("[Seed] Create a new Atlas Vector Search index with this JSON definition:")
    print()
    print("""    Index Name: meme_vector_index
    Database: grasschalant
    Collection: meme_vault
    Definition:
    {
      "fields": [
        {
          "type": "vector",
          "path": "embedding",
          "numDimensions": 512,
          "similarity": "cosine"
        }
      ]
    }""")
    print()
    print("[Seed] 🌿 Seeding complete!")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_memes())
