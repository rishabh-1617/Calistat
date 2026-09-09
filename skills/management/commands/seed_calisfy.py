from django.core.management.base import BaseCommand
from django.utils.text import slugify

from skills.models import SkillCategory, Skill, VerificationRequirement
from training.models import Exercise, Program, Workout, WorkoutExercise
from ranking.models import Rank, Achievement


class Command(BaseCommand):
    """Seed baseline reference data so the app isn't empty on first run."""
    help = "Seed Calisfy with comprehensive calisthenics skills, exercises, programs, ranks, and achievements."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding ranks...")
        self.seed_ranks()
        self.stdout.write("Seeding skill categories & skills...")
        self.seed_skills()
        self.stdout.write("Seeding exercises...")
        self.seed_exercises()
        self.stdout.write("Seeding training programs...")
        self.seed_programs()
        self.stdout.write("Seeding achievements...")
        self.seed_achievements()
        self.stdout.write(self.style.SUCCESS(
            "Calisfy fully seeded with all calisthenics skills, exercises, and programs."
        ))

    # ------------------------------------------------------------------
    # RANKS
    # ------------------------------------------------------------------
    def seed_ranks(self):
        ranks = [
            ("Novice",    1, "#8d8d8d",   0,  0,  0),
            ("Rookie",    2, "#8a9a5b", 500,  1,  2),
            ("Bronze",    3, "#cd7f32", 1500,  3,  8),
            ("Silver",    4, "#c0c0c0", 3500,  6, 20),
            ("Gold",      5, "#d4af37", 6500, 10, 40),
            ("Platinum",  6, "#4fd0e0", 10000, 15, 60),
            ("Elite",     7, "#e63946", 15000, 20, 90),
        ]
        for name, order, color, xp, vs, ss in ranks:
            Rank.objects.update_or_create(
                name=name,
                defaults=dict(order=order, badge_color=color, min_xp=xp,
                              min_verified_skills=vs, min_skill_score=ss),
            )
        self.stdout.write("  [OK] %d ranks" % len(ranks))

    # ------------------------------------------------------------------
    # SKILLS  (comprehensive, basics to elite)
    # ------------------------------------------------------------------
    def seed_skills(self):
        categories = {
            "Push":           1,
            "Pull":           2,
            "Core":           3,
            "Legs":           4,
            "Balance":        5,
            "Static Holds":   6,
            "Dynamic Skills": 7,
        }
        cat_objs = {}
        for name, order in categories.items():
            cat_objs[name], _ = SkillCategory.objects.update_or_create(
                name=name, defaults={"slug": slugify(name), "order": order}
            )

        # (name, category, difficulty_level, difficulty_score,
        #  [prerequisites], muscle_groups, description, common_mistakes)
        skills_data = [
            # -- PUSH -------------------------------------------------
            ("Wall Push-up", "Push", "beginner", 1, [],
             "Chest, Triceps, Shoulders",
             "Stand facing a wall and perform push-ups against it. Perfect for absolute beginners to build pushing strength.",
             "Flaring elbows too wide; not touching chest to wall."),

            ("Incline Push-up", "Push", "beginner", 1, ["Wall Push-up"],
             "Chest, Triceps, Shoulders",
             "Push-ups with hands elevated on a bench or step. Bridges the gap between wall and floor push-ups.",
             "Sagging hips; incomplete range of motion."),

            ("Push-up", "Push", "beginner", 2, ["Incline Push-up"],
             "Chest, Triceps, Shoulders, Core",
             "The classic floor push-up. Chest touches the ground, arms lock out at the top.",
             "Sagging lower back; not reaching full lockout; flared elbows."),

            ("Wide Push-up", "Push", "beginner", 2, ["Push-up"],
             "Chest, Shoulders",
             "Push-up with hands placed wider than shoulder width. Emphasizes chest activation.",
             "Dropping hips; insufficient depth."),

            ("Diamond Push-up", "Push", "beginner", 3, ["Push-up"],
             "Triceps, Inner Chest",
             "Hands close together forming a diamond shape. Heavy triceps emphasis.",
             "Elbows flaring out instead of staying close to body."),

            ("Decline Push-up", "Push", "intermediate", 3, ["Push-up"],
             "Upper Chest, Shoulders, Triceps",
             "Feet elevated on a bench. Shifts emphasis to upper chest and anterior deltoids.",
             "Excessive lower back arch; not maintaining body alignment."),

            ("Archer Push-up", "Push", "intermediate", 4, ["Diamond Push-up", "Wide Push-up"],
             "Chest, Triceps, Shoulders",
             "One arm performs the push-up while the other extends out for balance. Unilateral pushing strength.",
             "Rotating torso; bending the straight arm."),

            ("Pseudo Planche Push-up", "Push", "intermediate", 4, ["Diamond Push-up"],
             "Anterior Deltoids, Chest, Triceps",
             "Push-up with hands turned outward and placed near the hips. Key planche preparation drill.",
             "Hands too far forward; not leaning enough."),

            ("Pike Push-up", "Push", "intermediate", 4, ["Push-up"],
             "Shoulders, Triceps, Upper Chest",
             "Inverted V position push-up targeting overhead pressing strength. Prerequisite for handstand push-ups.",
             "Not bending elbows enough; hips not high enough."),

            ("Dips", "Push", "intermediate", 4, ["Push-up"],
             "Chest, Triceps, Shoulders",
             "Parallel bar dips with full range of motion. Fundamental upper body pushing exercise.",
             "Swinging; not going deep enough; excessive forward lean."),

            ("Ring Dips", "Push", "intermediate", 5, ["Dips"],
             "Chest, Triceps, Shoulders, Stabilizers",
             "Dips performed on gymnastic rings. Requires significant stabilizer strength.",
             "Rings flaring out; loss of turnout at top; insufficient depth."),

            ("One-arm Push-up", "Push", "advanced", 6, ["Archer Push-up"],
             "Chest, Triceps, Shoulders, Core",
             "Full push-up on a single arm. Requires exceptional unilateral pressing strength and core stability.",
             "Rotating hips; using wide leg stance as a crutch; incomplete ROM."),

            ("Handstand Push-up (Wall)", "Push", "advanced", 6, ["Pike Push-up"],
             "Shoulders, Triceps, Upper Chest, Core",
             "Full handstand push-up against a wall. Head touches ground, arms lock out.",
             "Kipping; arching back; not reaching full depth."),

            ("Handstand Push-up (Freestanding)", "Push", "advanced", 7, ["Handstand Push-up (Wall)", "Freestanding Handstand"],
             "Shoulders, Triceps, Core, Balance",
             "Handstand push-up without wall support. Combines pressing strength with balance mastery.",
             "Losing balance; kipping; bailing early."),

            ("Tiger Bend Push-up", "Push", "advanced", 7, ["Handstand Push-up (Wall)"],
             "Triceps, Shoulders",
             "From forearm support, extend to straight arms. Extreme triceps strength requirement.",
             "Using momentum; incomplete extension."),

            ("90 Degree Push-up", "Push", "elite", 8, ["Handstand Push-up (Freestanding)"],
             "Shoulders, Triceps, Core",
             "Push-up from a handstand down to a 90-degree arm bend and back up. Elite overhead strength.",
             "Arching; losing handstand alignment; kipping."),

            ("Planche Push-up", "Push", "elite", 9, ["Full Planche", "Pseudo Planche Push-up"],
             "Anterior Deltoids, Chest, Triceps, Core",
             "Push-up while maintaining a full planche position. One of the hardest push variations in calisthenics.",
             "Legs dropping; bending at hips; incomplete ROM."),

            ("Maltese Push-up", "Push", "elite", 10, ["Planche Push-up"],
             "Anterior Deltoids, Chest, Biceps, Core",
             "Push-up from a maltese hold (arms wide in planche). Pinnacle of pushing strength.",
             "Arms bending; hips dropping; insufficient hold."),

            # -- PULL -------------------------------------------------
            ("Dead Hang", "Pull", "beginner", 1, [],
             "Forearms, Grip, Shoulders",
             "Hang from a bar with straight arms. Builds grip endurance and shoulder mobility.",
             "Shrugging shoulders; bending arms; letting go too early."),

            ("Active Hang (Scapular Pull-up)", "Pull", "beginner", 1, ["Dead Hang"],
             "Lower Trapezius, Lats, Shoulders",
             "From dead hang, depress and retract scapulae without bending arms. Foundational pulling activation.",
             "Bending elbows; using momentum; insufficient range."),

            ("Australian Pull-up (Bodyweight Row)", "Pull", "beginner", 1, [],
             "Upper Back, Biceps, Rear Deltoids",
             "Horizontal rowing with feet on ground, body under a low bar. Scalable pulling exercise.",
             "Sagging hips; not pulling chest to bar; jerky motion."),

            ("Chin-up", "Pull", "beginner", 2, ["Active Hang (Scapular Pull-up)"],
             "Biceps, Lats, Forearms",
             "Pull-up with supinated (underhand) grip. Chin clears the bar. Stronger bicep involvement.",
             "Kipping; not clearing chin; incomplete dead hang at bottom."),

            ("Pull-up", "Pull", "beginner", 2, ["Active Hang (Scapular Pull-up)"],
             "Lats, Upper Back, Biceps, Forearms",
             "Pronated (overhand) grip pull-up. The gold standard of bodyweight pulling strength.",
             "Kipping; half reps; chin not clearing bar; crossed legs swinging."),

            ("Negative Pull-up", "Pull", "beginner", 2, ["Dead Hang"],
             "Lats, Upper Back, Biceps",
             "Jump or step to the top position and slowly lower down. Builds eccentric pulling strength.",
             "Dropping too fast; not controlling the descent."),

            ("Wide Grip Pull-up", "Pull", "intermediate", 3, ["Pull-up"],
             "Lats, Teres Major, Upper Back",
             "Pull-up with hands wider than shoulder width. Greater lat emphasis.",
             "Not pulling high enough; excessive swinging."),

            ("Close Grip Pull-up", "Pull", "intermediate", 3, ["Pull-up"],
             "Lats, Biceps, Forearms",
             "Pull-up with hands close together. Increased bicep and forearm engagement.",
             "Excessive body swing; not full range."),

            ("Chest-to-bar Pull-up", "Pull", "intermediate", 3, ["Pull-up"],
             "Lats, Upper Back, Biceps, Core",
             "Pull-up where chest touches the bar. Greater ROM builds explosive pulling power for muscle-ups.",
             "Not actually reaching chest to bar; using momentum."),

            ("L-sit Pull-up", "Pull", "intermediate", 4, ["Pull-up", "L-sit (Bar Hang)"],
             "Lats, Biceps, Core, Hip Flexors",
             "Pull-up while maintaining an L-sit position. Combines pulling strength with core control.",
             "Legs dropping during pull; swinging."),

            ("Typewriter Pull-up", "Pull", "intermediate", 5, ["Chest-to-bar Pull-up"],
             "Lats, Biceps, Forearms",
             "Pull to one side at the top of a pull-up, then traverse horizontally. Builds unilateral pulling strength.",
             "Not staying high enough; losing horizontal control."),

            ("Archer Pull-up", "Pull", "intermediate", 5, ["Typewriter Pull-up"],
             "Lats, Biceps, Upper Back",
             "One arm pulls while the other stays straight on the bar. Key one-arm pull-up progression.",
             "Bending the assistance arm; not full ROM."),

            ("Muscle-up (Bar)", "Pull", "advanced", 6, ["Chest-to-bar Pull-up"],
             "Lats, Chest, Triceps, Shoulders, Core",
             "Explosive pull-up transitioning over the bar into a dip. The signature calisthenics movement.",
             "Excessive kip; chicken-winging; not clearing the bar cleanly."),

            ("Muscle-up (Rings)", "Pull", "advanced", 7, ["Muscle-up (Bar)", "Ring Dips"],
             "Lats, Chest, Triceps, Shoulders, Stabilizers",
             "Muscle-up performed on gymnastic rings. Requires greater stabilization and false grip strength.",
             "Losing false grip; asymmetrical transition; rings flaring."),

            ("Weighted Pull-up", "Pull", "advanced", 5, ["Pull-up"],
             "Lats, Upper Back, Biceps",
             "Pull-up with additional weight (belt, vest, or backpack). Pure strength builder.",
             "Kipping with weight; half reps; too much weight too soon."),

            ("Front Lever Raises", "Pull", "advanced", 6, ["Tuck Front Lever"],
             "Lats, Core, Shoulders",
             "From dead hang, raise body to front lever position. Combines pulling and core strength.",
             "Bending arms; piking at hips; using momentum."),

            ("One-arm Chin-up", "Pull", "elite", 9, ["Archer Pull-up", "Weighted Pull-up"],
             "Lats, Biceps, Forearms, Core",
             "Full chin-up on a single arm. Among the most impressive feats of relative pulling strength.",
             "Using body rotation; half rep; excessive swing."),

            ("One-arm Pull-up", "Pull", "elite", 10, ["One-arm Chin-up"],
             "Lats, Biceps, Forearms, Core, Grip",
             "Full pull-up on a single arm with overhand grip. Ultimate pulling strength achievement.",
             "Excessive rotation; half reps; grip failure."),

            # -- CORE -------------------------------------------------
            ("Plank", "Core", "beginner", 1, [],
             "Transverse Abdominis, Rectus Abdominis, Obliques",
             "Hold a straight body position on forearms and toes. Foundational core endurance.",
             "Sagging hips; piking hips; holding breath."),

            ("Side Plank", "Core", "beginner", 1, ["Plank"],
             "Obliques, Transverse Abdominis",
             "Lateral plank on one forearm. Builds oblique strength and lateral stability.",
             "Dropping hip; rotating torso; collapsing shoulder."),

            ("Dead Bug", "Core", "beginner", 1, [],
             "Rectus Abdominis, Transverse Abdominis",
             "Lying supine, extend opposite arm and leg while keeping low back pressed to floor.",
             "Arching lower back; moving too fast; losing bracing."),

            ("Hollow Body Hold", "Core", "beginner", 2, ["Plank"],
             "Rectus Abdominis, Hip Flexors, Transverse Abdominis",
             "Lie on back with arms overhead, legs and shoulders lifted. Gymnastics foundation position.",
             "Lower back lifting off floor; bending knees; neck strain."),

            ("Knee Raise (Hanging)", "Core", "beginner", 2, ["Dead Hang"],
             "Hip Flexors, Lower Abs",
             "Hang from bar and raise knees to chest. Entry-level hanging core exercise.",
             "Swinging; using momentum; not controlling the negative."),

            ("Lying Leg Raise", "Core", "beginner", 2, [],
             "Lower Abs, Hip Flexors",
             "Lie on back and raise straight legs to vertical. Floor-based core strengthening.",
             "Lower back arching; bending knees; jerky movement."),

            ("Hanging Leg Raise", "Core", "intermediate", 3, ["Knee Raise (Hanging)"],
             "Lower Abs, Hip Flexors, Grip",
             "Hang from bar and raise straight legs to bar height. Requires significant hip flexor strength.",
             "Swinging; bending knees; not reaching full height."),

            ("Toes to Bar", "Core", "intermediate", 4, ["Hanging Leg Raise"],
             "Abs, Hip Flexors, Lats, Grip",
             "From dead hang, bring toes to touch the bar. Full range hanging core movement.",
             "Using momentum exclusively; losing grip; piking instead of compressing."),

            ("L-sit (Floor)", "Core", "intermediate", 3, ["Plank", "Lying Leg Raise"],
             "Hip Flexors, Abs, Triceps, Shoulders",
             "Sit with legs straight, press hands into floor and lift body. Hold legs parallel to floor.",
             "Bending knees; not fully lifting off ground; rounding back."),

            ("L-sit (Bar Hang)", "Core", "intermediate", 3, ["Hanging Leg Raise"],
             "Abs, Hip Flexors, Grip",
             "Hang from bar and hold legs at 90 degrees (parallel to floor). Core endurance builder.",
             "Legs dropping; excessive swinging; bending knees."),

            ("L-sit (Parallettes)", "Core", "intermediate", 4, ["L-sit (Floor)"],
             "Hip Flexors, Abs, Triceps, Shoulders",
             "L-sit on parallel bars or parallettes. Increased range allows cleaner form.",
             "Leaning too far back; bending knees; collapsed shoulders."),

            ("Windshield Wipers (Bent Knee)", "Core", "intermediate", 4, ["Hanging Leg Raise"],
             "Obliques, Abs, Grip",
             "Hang from bar, raise knees, and rotate them side to side. Rotational core strength.",
             "Losing control at the sides; excessive swinging."),

            ("Ab Wheel Rollout", "Core", "intermediate", 4, [],
             "Rectus Abdominis, Lats, Shoulders",
             "Roll an ab wheel out from kneeling or standing. Anti-extension core training.",
             "Collapsing at hips; lower back arching; not going deep enough."),

            ("Dragon Flag", "Core", "advanced", 6, ["Hanging Leg Raise", "Hollow Body Hold"],
             "Rectus Abdominis, Obliques, Hip Flexors",
             "Lie on bench, grip behind head, raise body from shoulders in one rigid line. Bruce Lee's signature exercise.",
             "Bending at hips; peeling off too early; not controlling the negative."),

            ("Windshield Wipers (Straight Leg)", "Core", "advanced", 6, ["Toes to Bar", "Windshield Wipers (Bent Knee)"],
             "Obliques, Abs, Hip Flexors, Grip",
             "Full straight-leg windshield wipers from a bar hang. Extreme rotational strength.",
             "Bending knees; losing control; grip failure."),

            ("V-sit", "Core", "advanced", 5, ["L-sit (Parallettes)"],
             "Hip Flexors, Abs, Compression Strength",
             "From L-sit, raise legs above horizontal into a V shape. Extreme hip flexor compression.",
             "Not achieving height; leaning too far back; shaking."),

            ("Hanging Windshield Wipers", "Core", "advanced", 6, ["Toes to Bar", "Windshield Wipers (Straight Leg)"],
             "Obliques, Abs, Lats, Grip",
             "Full body rotation side to side from a bar hang with straight legs. Elite rotational core.",
             "Using excessive momentum; bending knees; grip failure."),

            ("Human Flag", "Core", "elite", 8, ["Side Plank", "Pull-up", "Dips"],
             "Obliques, Lats, Shoulders, Full Body",
             "Hold body horizontal gripping a vertical pole. Full body lateral tension.",
             "Hips sagging; bending at waist; insufficient hold time."),

            ("Manna", "Core", "elite", 9, ["V-sit"],
             "Hip Flexors, Abs, Shoulders, Compression",
             "From seated position, press body up with legs raised behind and above. Gymnastics pinnacle.",
             "Insufficient hip flexibility; cannot elevate legs past 45 degrees."),

            # -- LEGS -------------------------------------------------
            ("Bodyweight Squat", "Legs", "beginner", 1, [],
             "Quadriceps, Glutes, Hamstrings",
             "Full depth squat with bodyweight only. Foundational lower body movement.",
             "Knees caving inward; heels rising; not reaching depth."),

            ("Lunge", "Legs", "beginner", 1, [],
             "Quadriceps, Glutes, Hamstrings",
             "Step forward into a split stance and lower back knee toward ground. Unilateral leg strength.",
             "Front knee passing toes excessively; losing balance; torso collapsing."),

            ("Glute Bridge", "Legs", "beginner", 1, [],
             "Glutes, Hamstrings, Core",
             "Lie on back, feet flat, drive hips upward. Glute activation and posterior chain builder.",
             "Hyperextending lower back; not squeezing at top; feet too far out."),

            ("Step-up", "Legs", "beginner", 1, [],
             "Quadriceps, Glutes",
             "Step up onto an elevated platform one leg at a time. Builds unilateral strength and balance.",
             "Pushing off back foot; not controlling the step down."),

            ("Calf Raise", "Legs", "beginner", 1, [],
             "Gastrocnemius, Soleus",
             "Rise up onto the balls of the feet. Targeted calf strengthening.",
             "Not going through full range; bouncing at bottom."),

            ("Wall Sit", "Legs", "beginner", 2, ["Bodyweight Squat"],
             "Quadriceps, Glutes",
             "Back against wall, thighs parallel to floor. Isometric quad endurance builder.",
             "Knees past toes; not reaching 90 degrees; sliding down."),

            ("Jump Squat", "Legs", "intermediate", 3, ["Bodyweight Squat"],
             "Quadriceps, Glutes, Calves",
             "Explosive squat with a jump at the top. Builds lower body power.",
             "Landing with stiff knees; not reaching squat depth; poor landing mechanics."),

            ("Bulgarian Split Squat", "Legs", "intermediate", 3, ["Lunge"],
             "Quadriceps, Glutes, Hamstrings",
             "Rear foot elevated on a bench, perform a single-leg squat. Superior unilateral leg builder.",
             "Leaning too far forward; rear foot bearing too much weight."),

            ("Single Leg Glute Bridge", "Legs", "intermediate", 3, ["Glute Bridge"],
             "Glutes, Hamstrings, Core",
             "Glute bridge with one leg extended. Addresses bilateral imbalances.",
             "Rotating hips; cramping hamstring; not full hip extension."),

            ("Nordic Curl (Eccentric)", "Legs", "intermediate", 4, [],
             "Hamstrings, Glutes",
             "Kneel, anchor feet, slowly lower body forward using hamstrings to control descent.",
             "Falling forward uncontrolled; bending at hips instead of knees."),

            ("Sissy Squat", "Legs", "intermediate", 4, ["Bodyweight Squat"],
             "Quadriceps, Hip Flexors",
             "Lean back while squatting with knees traveling far forward. Extreme quad isolation.",
             "Using hands for support; not reaching full depth; knee pain (go slow)."),

            ("Box Pistol Squat", "Legs", "intermediate", 4, ["Bulgarian Split Squat"],
             "Quadriceps, Glutes, Balance",
             "Single-leg squat down to a box or bench. Pistol squat progression.",
             "Collapsing at bottom; non-working leg touching ground."),

            ("Shrimp Squat (Assisted)", "Legs", "intermediate", 4, ["Bulgarian Split Squat"],
             "Quadriceps, Glutes, Balance",
             "Single-leg squat holding rear foot behind, using support. Shrimp squat progression.",
             "Leaning too far forward; losing grip on rear foot."),

            ("Pistol Squat", "Legs", "advanced", 5, ["Box Pistol Squat"],
             "Quadriceps, Glutes, Hamstrings, Balance",
             "Full single-leg squat with the other leg extended forward. Iconic bodyweight leg exercise.",
             "Heel rising; rounding lower back; losing balance at bottom."),

            ("Shrimp Squat (Full)", "Legs", "advanced", 6, ["Shrimp Squat (Assisted)"],
             "Quadriceps, Glutes, Balance, Flexibility",
             "Full shrimp squat with rear knee touching the ground behind. Extreme single-leg control.",
             "Not reaching full depth; losing balance; excessive forward lean."),

            ("Nordic Curl (Full)", "Legs", "advanced", 6, ["Nordic Curl (Eccentric)"],
             "Hamstrings, Glutes",
             "Full concentric and eccentric nordic curl. One of the hardest hamstring exercises.",
             "Using hands to push up; hinging at hips; incomplete range."),

            ("Natural Leg Extension", "Legs", "advanced", 6, [],
             "Quadriceps",
             "Reverse nordic curl -- lean back from kneeling position. Pure quad strength.",
             "Not controlling the lean; insufficient range; pain at patella."),

            ("Dragon Pistol Squat", "Legs", "elite", 8, ["Pistol Squat"],
             "Quadriceps, Glutes, Hamstrings, Core, Balance",
             "Pistol squat with the non-working leg wrapped behind the working leg. Extreme balance and control.",
             "Falling sideways; insufficient ankle flexibility; lack of depth."),

            # -- BALANCE ----------------------------------------------
            ("Crow Pose (Frog Stand)", "Balance", "beginner", 2, [],
             "Shoulders, Core, Wrists",
             "Balance on hands with knees resting on back of upper arms. Entry-level arm balance.",
             "Face-planting; not leaning forward enough; wrist pain."),

            ("Headstand", "Balance", "beginner", 2, [],
             "Shoulders, Core, Neck",
             "Supported inverted balance on head and forearms (tripod or forearm headstand).",
             "Kicking up too hard; losing alignment; neck compression."),

            ("Wall Handstand", "Balance", "beginner", 2, [],
             "Shoulders, Triceps, Core, Wrists",
             "Handstand against a wall (chest or back to wall). Builds overhead endurance and alignment.",
             "Banana back; not engaging shoulders; wrist pain."),

            ("Elbow Lever", "Balance", "intermediate", 3, ["Crow Pose (Frog Stand)"],
             "Core, Shoulders, Wrists, Forearms",
             "Balance horizontally on bent arms with elbow dug into hip. A dramatic lever balance.",
             "Not finding the balance point; wrist strain; hips too low."),

            ("Freestanding Handstand", "Balance", "intermediate", 5, ["Wall Handstand"],
             "Shoulders, Core, Wrists, Full Body Balance",
             "Handstand without wall support. The cornerstone balance skill of calisthenics.",
             "Over-balancing; banana back; not using fingers to correct."),

            ("Handstand Walk", "Balance", "advanced", 6, ["Freestanding Handstand"],
             "Shoulders, Core, Wrists",
             "Walk on hands while maintaining a handstand. Dynamic balance control.",
             "Falling sideways; inconsistent steps; losing alignment."),

            ("Press to Handstand (Straddle)", "Balance", "advanced", 7, ["Freestanding Handstand", "L-sit (Parallettes)"],
             "Shoulders, Core, Hip Flexors, Hamstrings",
             "From standing or L-sit, press slowly into handstand with straddled legs. Strength + flexibility.",
             "Jumping instead of pressing; insufficient hamstring flexibility."),

            ("Press to Handstand (Pike)", "Balance", "elite", 8, ["Press to Handstand (Straddle)"],
             "Shoulders, Core, Hip Flexors, Compression",
             "Press to handstand with legs together. Requires extreme compression strength.",
             "Unable to clear the floor; breaking form halfway."),

            ("One-arm Handstand", "Balance", "elite", 10, ["Freestanding Handstand", "Handstand Walk"],
             "Shoulders, Core, Wrists, Full Body",
             "Full handstand balanced on a single arm. Years of dedicated balance training required.",
             "Falling immediately; over-rotation; excessive hip shift."),

            ("Handstand on Rings", "Balance", "elite", 9, ["Freestanding Handstand", "Ring Dips"],
             "Shoulders, Core, Stabilizers",
             "Full handstand performed on gymnastic rings. Extreme instability demands mastery.",
             "Rings wobbling out; losing alignment; fear of falling."),

            # -- STATIC HOLDS -----------------------------------------
            ("Tuck Front Lever", "Static Holds", "intermediate", 3, ["Pull-up", "Hollow Body Hold"],
             "Lats, Core, Shoulders",
             "Hang from bar, body horizontal with knees tucked to chest. Entry front lever progression.",
             "Hips dropping; not maintaining horizontal; rounding back."),

            ("Advanced Tuck Front Lever", "Static Holds", "intermediate", 4, ["Tuck Front Lever"],
             "Lats, Core, Shoulders",
             "Front lever with hips extended but knees still bent. Greater lat engagement.",
             "Hips sagging; back rounding; unable to hold position."),

            ("Straddle Front Lever", "Static Holds", "advanced", 6, ["Advanced Tuck Front Lever"],
             "Lats, Core, Shoulders, Rear Deltoids",
             "Front lever with legs straddled wide. Significant increase in lever difficulty.",
             "One leg dropping; hips not level; insufficient hold time."),

            ("Full Front Lever", "Static Holds", "elite", 8, ["Straddle Front Lever"],
             "Lats, Core, Shoulders, Full Posterior Chain",
             "Body held perfectly horizontal from bar with straight legs together. Elite static hold.",
             "Hips sagging; body not horizontal; hold too short."),

            ("Front Lever Pull-up", "Static Holds", "elite", 9, ["Full Front Lever"],
             "Lats, Core, Biceps, Shoulders",
             "Pull-up performed from and returning to a full front lever. Ultimate pulling strength demonstration.",
             "Losing lever during pull; kicking legs."),

            ("Tuck Back Lever", "Static Holds", "intermediate", 3, ["Skin the Cat"],
             "Shoulders, Biceps, Core",
             "Hang inverted behind the bar with knees tucked. Entry back lever progression.",
             "Excessive shoulder strain (go slowly); not maintaining tuck."),

            ("Full Back Lever", "Static Holds", "advanced", 5, ["Tuck Back Lever"],
             "Shoulders, Biceps, Core, Chest",
             "Body held horizontal behind the bar with straight legs. Requires excellent shoulder flexibility.",
             "Insufficient shoulder mobility; body not horizontal."),

            ("Tuck Planche", "Static Holds", "intermediate", 4, ["Pseudo Planche Push-up", "L-sit (Floor)"],
             "Anterior Deltoids, Core, Chest, Triceps",
             "Support body horizontal on straight arms with knees tucked. Entry planche progression.",
             "Not leaning forward enough; hips too low; wrist pain."),

            ("Advanced Tuck Planche", "Static Holds", "intermediate", 5, ["Tuck Planche"],
             "Anterior Deltoids, Core, Chest",
             "Planche with hips open but knees bent. Increased lever arm and difficulty.",
             "Back rounding; hips not opening; arms bending."),

            ("Straddle Planche", "Static Holds", "advanced", 7, ["Advanced Tuck Planche"],
             "Anterior Deltoids, Core, Chest, Triceps",
             "Planche with legs straddled. Significant strength milestone.",
             "Legs not high enough; hips dropping; arms bending."),

            ("Full Planche", "Static Holds", "elite", 9, ["Straddle Planche"],
             "Anterior Deltoids, Core, Chest, Triceps, Full Body",
             "Body held horizontal on straight arms with legs together. Pinnacle calisthenics static hold.",
             "Legs dropping; arms bending; insufficient hold time."),

            ("Iron Cross", "Static Holds", "elite", 10, ["Ring Dips", "Full Front Lever"],
             "Chest, Biceps, Shoulders, Lats",
             "Hold rings at shoulder height with arms straight out to the sides. Iconic gymnastics strength position.",
             "Arms bending; rings drifting; insufficient connective tissue preparation."),

            ("Victorian Cross", "Static Holds", "elite", 10, ["Iron Cross"],
             "Shoulders, Chest, Biceps, Core",
             "Inverted iron cross -- arms behind body on rings while body faces down. Ultra-elite ring skill.",
             "Shoulder injury risk if rushed; arms bending."),

            ("Maltese", "Static Holds", "elite", 10, ["Full Planche", "Iron Cross"],
             "Anterior Deltoids, Chest, Biceps, Core",
             "Planche with arms out to the sides. Combines planche and iron cross demands.",
             "Insufficient shoulder preparation; arms bending; body not horizontal."),

            # -- DYNAMIC SKILLS ---------------------------------------
            ("Skin the Cat", "Dynamic Skills", "beginner", 2, ["Dead Hang", "Active Hang (Scapular Pull-up)"],
             "Shoulders, Lats, Core",
             "From hang, rotate body backward through arms to inverted hang and back. Shoulder mobility builder.",
             "Going too fast; insufficient shoulder flexibility; losing grip."),

            ("Kipping Pull-up", "Dynamic Skills", "beginner", 2, ["Pull-up"],
             "Lats, Shoulders, Core, Hip Drive",
             "Pull-up using a rhythmic hip swing for momentum. CrossFit staple for reps/conditioning.",
             "No actual pulling strength engagement; excessive kip."),

            ("Kip-up (Ground)", "Dynamic Skills", "intermediate", 3, [],
             "Hip Flexors, Core, Shoulders, Explosive Power",
             "From lying on back, explosively kip up to standing. Dynamic bodyweight skill.",
             "Not generating enough hip power; landing off-balance."),

            ("Bar Muscle-up (Kipping)", "Dynamic Skills", "intermediate", 4, ["Kipping Pull-up", "Chest-to-bar Pull-up"],
             "Lats, Chest, Triceps, Hip Drive",
             "Muscle-up with kipping momentum. More accessible than strict muscle-up.",
             "Too much swing; not clearing bar; catching too low."),

            ("360 Pull-up", "Dynamic Skills", "advanced", 7, ["Muscle-up (Bar)"],
             "Lats, Grip, Core, Full Body Coordination",
             "Explosive pull-up with a full 360-degree rotation around the bar. Freestyle calisthenics move.",
             "Not enough height; losing grip; improper rotation."),

            ("Giant Swing", "Dynamic Skills", "advanced", 7, ["Muscle-up (Bar)"],
             "Shoulders, Core, Grip, Full Body",
             "Full 360-degree rotation around the bar from support. Gymnastics high bar skill.",
             "Losing momentum; improper timing; bar slip."),

            ("Felge (Cast to Handstand)", "Dynamic Skills", "advanced", 6, ["Muscle-up (Bar)", "Handstand Push-up (Wall)"],
             "Shoulders, Core, Lats",
             "From support on bar, cast body up and over into handstand on bar. Gymnastics foundation.",
             "Insufficient cast height; losing alignment; missing handstand."),

            ("Hefesto (Reverse Muscle-up)", "Dynamic Skills", "elite", 8, ["Muscle-up (Bar)", "Full Back Lever"],
             "Biceps, Shoulders, Core",
             "From hang facing away, rotate up and over the bar backwards into support. Extreme skill.",
             "Shoulder strain; insufficient back lever strength; losing grip."),

            ("Geinger", "Dynamic Skills", "elite", 9, ["Giant Swing"],
             "Full Body Coordination, Core, Grip, Explosive Power",
             "Release bar, perform a backflip, and re-catch the bar. High bar release move.",
             "Missing the catch; insufficient height; fear commitment."),
        ]

        skill_objs = {}
        count = 0
        for name, cat, level, score, _prereqs, muscles, desc, mistakes in skills_data:
            skill, _ = Skill.objects.update_or_create(
                name=name,
                defaults=dict(
                    slug=slugify(name), category=cat_objs[cat],
                    difficulty_level=level, difficulty_score=score,
                    description=desc,
                    muscle_groups=muscles,
                    technique_instructions="",
                    common_mistakes=mistakes,
                ),
            )
            skill_objs[name] = skill
            count += 1

        # Wire up prerequisites & progressions
        for name, _cat, _level, _score, prereqs, *_ in skills_data:
            skill = skill_objs[name]
            for p in prereqs:
                if p in skill_objs:
                    skill.prerequisites.add(skill_objs[p])
                    skill_objs[p].progresses_to.add(skill)

        self.stdout.write("  [OK] %d skills across %d categories" % (count, len(categories)))

        # -- Verification Requirements for advanced/elite skills --
        strict_skills = [
            ("Muscle-up (Bar)",
             "Show full body, full bar, starting from dead hang, full pull, clean transition over bar, and full lockout in one uncut take.",
             False, None, 1),
            ("Muscle-up (Rings)",
             "Show full body and rings, false grip, dead hang start, clean transition and lockout. One uncut take.",
             True, None, 1),
            ("Full Front Lever",
             "Fixed camera angle showing full body horizontal with straight legs. Minimum 3 second hold, no cuts.",
             True, 3, None),
            ("Full Planche",
             "Fixed camera angle showing full body horizontal on straight arms with legs together. Minimum 3 second hold, no cuts.",
             True, 3, None),
            ("Straddle Planche",
             "Fixed camera showing full straddle planche position on straight arms. Minimum 3 second hold.",
             True, 3, None),
            ("Iron Cross",
             "Show full body on rings with arms straight out at shoulder height. Minimum 2 second hold, no cuts.",
             True, 2, None),
            ("One-arm Pull-up",
             "Show full body, single arm on bar, dead hang start, chin above bar, controlled negative. No cuts.",
             True, None, 1),
            ("One-arm Chin-up",
             "Show full body, single arm supinated grip, dead hang start, chin above bar. No cuts.",
             True, None, 1),
            ("Handstand Push-up (Freestanding)",
             "Show full body freestanding handstand, head touches ground, full lockout. No wall, no cuts.",
             True, None, 1),
            ("One-arm Handstand",
             "Fixed camera showing full one-arm handstand. Minimum 3 second hold, no wall support.",
             True, 3, None),
            ("Human Flag",
             "Fixed camera showing full body horizontal on vertical pole. Minimum 3 second hold.",
             True, 3, None),
            ("Pistol Squat",
             "Show full depth single-leg squat with other leg extended. Full standing lockout. No support.",
             False, None, 1),
            ("Dragon Flag",
             "Show from bench/floor, full body rigid, controlled negative and positive. No cuts.",
             False, None, 1),
            ("Full Back Lever",
             "Fixed camera showing body horizontal behind bar with straight legs. Minimum 3 second hold.",
             True, 3, None),
            ("Maltese",
             "Show full maltese hold on rings or floor. Arms wide, body horizontal. Minimum 2 second hold.",
             True, 2, None),
            ("Victorian Cross",
             "Show inverted cross on rings from fixed camera. Minimum 2 second hold.",
             True, 2, None),
            ("Manna",
             "Show full manna position from floor or parallettes. Legs above horizontal behind body. Minimum 2 second hold.",
             True, 2, None),
            ("Front Lever Pull-up",
             "Show full front lever pull-up: start from lever, pull to bar, return to lever. No cuts.",
             True, None, 1),
            ("Hefesto (Reverse Muscle-up)",
             "Show full reverse muscle-up from dead hang to support. Uncut take from fixed camera.",
             True, None, 1),
            ("Planche Push-up",
             "Show planche push-up: lower from planche, press back up. Full ROM, no cuts.",
             True, None, 1),
        ]
        for sname, instructions, strict, hold, reps in strict_skills:
            if sname in skill_objs:
                VerificationRequirement.objects.update_or_create(
                    skill=skill_objs[sname],
                    defaults=dict(
                        instructions=instructions,
                        requires_strict_review=strict,
                        min_hold_seconds=hold,
                        min_reps=reps,
                    ),
                )
        self.stdout.write("  [OK] %d verification requirements" % len(strict_skills))

    # ------------------------------------------------------------------
    # EXERCISES (library for use inside workouts)
    # ------------------------------------------------------------------
    def seed_exercises(self):
        # (name, description, related_skill_name_or_None)
        exercises = [
            # -- Warm-up / Mobility --
            ("Arm Circles", "Controlled forward and backward arm circles to warm up shoulders.", None),
            ("Wrist Circles", "Rotate wrists in both directions. Essential before any hand balancing.", None),
            ("Cat-Cow Stretch", "Alternate between arching and rounding the spine on all fours.", None),
            ("Shoulder Dislocates (Band/Stick)", "Pass a band or stick overhead and behind for shoulder mobility.", None),
            ("Hip Circles", "Standing hip circles to warm up hip joints.", None),
            ("Leg Swings (Front-Back)", "Dynamic forward/backward leg swings for hamstrings and hip flexors.", None),
            ("Leg Swings (Side-Side)", "Dynamic lateral leg swings for adductors and abductors.", None),
            ("Band Pull-aparts", "Pull resistance band apart at chest height. Rear delt and scap activation.", None),
            ("Inchworm", "Walk hands forward from standing to plank and walk back. Full body warm-up.", None),
            ("World's Greatest Stretch", "Lunge with thoracic rotation. Comprehensive mobility drill.", None),

            # -- Push Exercises --
            ("Wall Push-ups", "Push-ups against a wall. Beginner regression.", "Wall Push-up"),
            ("Incline Push-ups", "Push-ups on an elevated surface.", "Incline Push-up"),
            ("Standard Push-ups", "Classic floor push-ups.", "Push-up"),
            ("Diamond Push-ups", "Close-grip push-ups targeting triceps.", "Diamond Push-up"),
            ("Wide Push-ups", "Wide-grip push-ups targeting chest.", "Wide Push-up"),
            ("Decline Push-ups", "Feet-elevated push-ups.", "Decline Push-up"),
            ("Archer Push-ups", "Side-to-side push-ups.", "Archer Push-up"),
            ("Pseudo Planche Push-ups", "Hands by hips, lean forward push-ups.", "Pseudo Planche Push-up"),
            ("Pike Push-ups", "Inverted V push-ups targeting shoulders.", "Pike Push-up"),
            ("Parallel Bar Dips", "Dips on parallel bars.", "Dips"),
            ("Ring Dip Exercise", "Dips on gymnastic rings.", "Ring Dips"),
            ("Wall Handstand Push-ups", "Handstand push-ups against wall.", "Handstand Push-up (Wall)"),
            ("Elevated Pike Push-ups", "Feet on high surface, pike push-up. HSPU progression.", "Pike Push-up"),
            ("Straight Bar Dips", "Dips on a straight bar (pull-up bar). Muscle-up transition work.", "Muscle-up (Bar)"),
            ("Ring Push-ups", "Push-ups on rings for instability training.", None),
            ("Hindu Push-ups", "Flowing push-up combining downward dog and cobra. Shoulder mobility.", None),
            ("Clap Push-ups", "Explosive push-up with a clap at the top. Power building.", None),

            # -- Pull Exercises --
            ("Dead Hangs", "Passive hang from bar. Grip and shoulder health.", "Dead Hang"),
            ("Active Hangs (Scapular Pull-ups)", "Engage scapulae from dead hang without bending arms.", "Active Hang (Scapular Pull-up)"),
            ("Australian Pull-ups (Bodyweight Rows)", "Horizontal rows under a low bar.", "Australian Pull-up (Bodyweight Row)"),
            ("Negative Pull-ups", "Slow lowering from top of pull-up.", "Negative Pull-up"),
            ("Chin-ups", "Underhand grip pull-ups.", "Chin-up"),
            ("Pull-ups", "Standard overhand grip pull-ups.", "Pull-up"),
            ("Wide Grip Pull-ups", "Pull-ups with wide hand placement.", "Wide Grip Pull-up"),
            ("Close Grip Pull-ups", "Pull-ups with narrow hand placement.", "Close Grip Pull-up"),
            ("Chest-to-bar Pull-ups", "Pull-ups where chest touches bar.", "Chest-to-bar Pull-up"),
            ("L-sit Pull-ups", "Pull-ups while holding L-sit.", "L-sit Pull-up"),
            ("Typewriter Pull-ups", "Traverse side-to-side at top of pull-up.", "Typewriter Pull-up"),
            ("Archer Pull-ups", "One arm pulls, other stays straight.", "Archer Pull-up"),
            ("Explosive Pull-ups", "Pull-up with explosive intent -- hands may leave bar.", None),
            ("Band-assisted Muscle-ups", "Muscle-up with resistance band assistance.", "Muscle-up (Bar)"),
            ("Bar Muscle-ups", "Strict muscle-up over the bar.", "Muscle-up (Bar)"),
            ("Ring Muscle-ups", "Muscle-up on gymnastics rings.", "Muscle-up (Rings)"),
            ("False Grip Hangs", "Dead hang on rings with false grip. Prep for ring muscle-up.", "Muscle-up (Rings)"),
            ("Towel Pull-ups", "Pull-ups gripping a towel. Grip strength builder.", None),

            # -- Core Exercises --
            ("Plank Hold", "Standard forearm or straight-arm plank.", "Plank"),
            ("Side Plank Hold", "Lateral plank on one forearm.", "Side Plank"),
            ("Dead Bugs", "Supine alternating opposite arm/leg extension.", "Dead Bug"),
            ("Hollow Body Holds", "Supine, arms overhead, legs and shoulders lifted.", "Hollow Body Hold"),
            ("Hollow Body Rocks", "Rocking in hollow body position. Core endurance.", "Hollow Body Hold"),
            ("Hanging Knee Raises", "Knees to chest from bar hang.", "Knee Raise (Hanging)"),
            ("Hanging Leg Raises", "Straight legs to bar height from hang.", "Hanging Leg Raise"),
            ("Toes to Bar Exercise", "Bring toes to touch the bar.", "Toes to Bar"),
            ("Floor L-sit Holds", "L-sit on the floor with straight arms.", "L-sit (Floor)"),
            ("Parallette L-sit Holds", "L-sit on parallettes.", "L-sit (Parallettes)"),
            ("Ab Wheel Rollouts", "Roll ab wheel out and back from kneeling.", "Ab Wheel Rollout"),
            ("Dragon Flags", "Full body flag from bench. Controlled negative.", "Dragon Flag"),
            ("V-sit Holds", "Hold V-sit on parallettes or floor.", "V-sit"),
            ("Lying Leg Raises", "Straight leg raises from lying position.", "Lying Leg Raise"),
            ("Bicycle Crunches", "Alternating elbow-to-knee crunch. Oblique work.", None),
            ("Mountain Climbers", "Alternating knee drives from plank position. Core + cardio.", None),
            ("Pallof Press (Band)", "Anti-rotation press with resistance band. Core stability.", None),
            ("Copenhagen Plank", "Side plank with top foot on elevated surface. Adductor + oblique work.", None),

            # -- Leg Exercises --
            ("Bodyweight Squats", "Standard air squats to full depth.", "Bodyweight Squat"),
            ("Jump Squats", "Explosive squat with jump.", "Jump Squat"),
            ("Walking Lunges", "Continuous forward lunges.", "Lunge"),
            ("Reverse Lunges", "Step-back lunges.", "Lunge"),
            ("Bulgarian Split Squats", "Rear foot elevated split squat.", "Bulgarian Split Squat"),
            ("Glute Bridges", "Hip thrust from floor.", "Glute Bridge"),
            ("Single Leg Glute Bridges", "One-leg hip thrust.", "Single Leg Glute Bridge"),
            ("Step-ups", "Step onto elevated platform.", "Step-up"),
            ("Wall Sits", "Isometric squat against wall.", "Wall Sit"),
            ("Calf Raises", "Rise up on the balls of the feet.", "Calf Raise"),
            ("Single Leg Calf Raises", "Calf raise on one leg.", "Calf Raise"),
            ("Sissy Squats", "Lean-back quad isolation squat.", "Sissy Squat"),
            ("Pistol Squats", "Full single-leg squat.", "Pistol Squat"),
            ("Box Pistol Squats", "Pistol squat to a box.", "Box Pistol Squat"),
            ("Assisted Shrimp Squats", "Shrimp squat with support.", "Shrimp Squat (Assisted)"),
            ("Nordic Curls (Eccentric)", "Slow negative hamstring curl.", "Nordic Curl (Eccentric)"),
            ("Nordic Curls (Full)", "Full concentric + eccentric.", "Nordic Curl (Full)"),
            ("Natural Leg Extensions", "Reverse nordic curl.", "Natural Leg Extension"),
            ("Broad Jumps", "Horizontal explosive jump. Lower body power.", None),
            ("Single Leg RDL", "Single-leg Romanian deadlift with bodyweight.", None),

            # -- Balance / Handstand Drills --
            ("Crow Pose Holds", "Hold crow pose (frog stand).", "Crow Pose (Frog Stand)"),
            ("Wall Handstand Holds", "Chest-to-wall or back-to-wall handstand.", "Wall Handstand"),
            ("Handstand Kick-ups", "Practice kicking up to freestanding handstand.", "Freestanding Handstand"),
            ("Handstand Toe Pulls (Wall)", "Chest to wall, pull toes off one at a time for balance.", "Freestanding Handstand"),
            ("Handstand Shoulder Taps", "From wall handstand, tap shoulders alternately.", "Wall Handstand"),
            ("Freestanding Handstand Hold", "Practice freestanding handstand balance.", "Freestanding Handstand"),
            ("Handstand Walking", "Walk on hands.", "Handstand Walk"),
            ("Headstand Hold", "Tripod or forearm headstand.", "Headstand"),
            ("Elbow Lever Hold", "Balance on bent arms in lever position.", "Elbow Lever"),

            # -- Static Hold Drills --
            ("Tuck Front Lever Holds", "Hold tuck front lever.", "Tuck Front Lever"),
            ("Advanced Tuck FL Holds", "Hold advanced tuck front lever.", "Advanced Tuck Front Lever"),
            ("Straddle Front Lever Holds", "Hold straddle front lever.", "Straddle Front Lever"),
            ("Front Lever Negatives", "Lower slowly from inverted hang to front lever.", "Full Front Lever"),
            ("Tuck Planche Holds", "Hold tuck planche.", "Tuck Planche"),
            ("Advanced Tuck Planche Holds", "Hold advanced tuck planche.", "Advanced Tuck Planche"),
            ("Planche Lean Push-ups", "Push-up with planche lean. Builds straight-arm pressing.", "Tuck Planche"),
            ("Tuck Back Lever Holds", "Hold tuck back lever.", "Tuck Back Lever"),
            ("Skin the Cats", "Full rotation through hang behind bar.", "Skin the Cat"),
            ("Band-assisted Front Lever", "Front lever with resistance band support.", "Full Front Lever"),
            ("Band-assisted Planche", "Planche with resistance band support.", "Full Planche"),

            # -- Flexibility / Cooldown --
            ("Pike Stretch", "Seated forward fold targeting hamstrings.", None),
            ("Straddle Stretch", "Seated straddle stretch for adductors.", None),
            ("Shoulder Stretch (Cross-body)", "Cross-body shoulder stretch.", None),
            ("Chest Stretch (Doorway)", "Stretch chest and anterior deltoids in doorway.", None),
            ("Wrist Flexor/Extensor Stretches", "Stretch wrists in both directions. Essential after hand balancing.", None),
            ("Figure Four Hip Stretch", "Lie on back, ankle on knee, pull knee to chest.", None),
            ("Couch Stretch", "Hip flexor stretch with rear foot elevated on wall/couch.", None),
            ("Pancake Stretch", "Seated straddle with chest to floor. Essential for press handstand and straddle skills.", None),
            ("German Hang Stretch", "Hang behind bar with feet on ground. Shoulder extension stretch.", None),
            ("Bridge (Backbend)", "Full gymnastic bridge for spine and shoulder flexibility.", None),
        ]

        skill_cache = {}
        count = 0
        for name, desc, related_skill_name in exercises:
            related = None
            if related_skill_name:
                if related_skill_name not in skill_cache:
                    skill_cache[related_skill_name] = Skill.objects.filter(name=related_skill_name).first()
                related = skill_cache[related_skill_name]
            Exercise.objects.update_or_create(
                name=name,
                defaults=dict(description=desc, related_skill=related),
            )
            count += 1
        self.stdout.write("  [OK] %d exercises" % count)

    # ------------------------------------------------------------------
    # TRAINING PROGRAMS
    # ------------------------------------------------------------------
    def seed_programs(self):
        self._seed_foundations_program()
        self._seed_muscle_up_program()
        self._seed_handstand_program()
        self._seed_front_lever_program()
        self._seed_planche_program()
        self._seed_full_body_program()

    def _make_workout(self, program, title, duration, order, exercises):
        """Helper: create a workout and its exercises."""
        workout, _ = Workout.objects.update_or_create(
            program=program, title=title,
            defaults=dict(estimated_duration_minutes=duration, order_in_program=order),
        )
        for i, (ex_name, section, sets, reps, rest) in enumerate(exercises):
            exercise, _ = Exercise.objects.get_or_create(name=ex_name)
            WorkoutExercise.objects.update_or_create(
                workout=workout, exercise=exercise,
                defaults=dict(section=section, sets=sets, reps=reps, rest_seconds=rest, order=i),
            )
        return workout

    # -- 1. Beginner Calisthenics Foundations (6 weeks) --
    def _seed_foundations_program(self):
        program, _ = Program.objects.update_or_create(
            name="Beginner Calisthenics Foundations",
            defaults=dict(
                description="A 6-week program for complete beginners. Build baseline pushing, pulling, and core strength with proper form before advancing to harder skills.",
                target_skill=Skill.objects.filter(name="Pull-up").first(),
                experience_level="beginner",
                duration_weeks=6, days_per_week=3,
            ),
        )
        self._make_workout(program, "Foundations -- Push Day", 30, 1, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Wrist Circles", "warmup", 2, "10 each direction", 0),
            ("Incline Push-ups", "strength", 3, "10-12", 60),
            ("Standard Push-ups", "strength", 3, "8-10", 60),
            ("Parallel Bar Dips", "strength", 3, "5-8 (or negatives)", 90),
            ("Plank Hold", "core", 3, "30s", 30),
            ("Pike Stretch", "cooldown", 2, "30s hold", 0),
        ])
        self._make_workout(program, "Foundations -- Pull Day", 30, 2, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Band Pull-aparts", "warmup", 2, "15", 0),
            ("Dead Hangs", "skill", 3, "20-30s", 30),
            ("Australian Pull-ups (Bodyweight Rows)", "strength", 3, "10-12", 60),
            ("Negative Pull-ups", "strength", 3, "5 (5s lower)", 90),
            ("Hollow Body Holds", "core", 3, "20s", 30),
            ("Shoulder Stretch (Cross-body)", "cooldown", 2, "30s each arm", 0),
        ])
        self._make_workout(program, "Foundations -- Legs & Core", 30, 3, [
            ("Hip Circles", "warmup", 2, "10 each direction", 0),
            ("Leg Swings (Front-Back)", "warmup", 2, "10 each leg", 0),
            ("Bodyweight Squats", "strength", 3, "15", 60),
            ("Walking Lunges", "strength", 3, "12 each leg", 60),
            ("Glute Bridges", "strength", 3, "15", 60),
            ("Hanging Knee Raises", "core", 3, "10", 45),
            ("Dead Bugs", "core", 3, "10 each side", 30),
            ("Figure Four Hip Stretch", "cooldown", 2, "30s each side", 0),
        ])
        self.stdout.write("  [OK] Beginner Calisthenics Foundations (6 weeks, 3 workouts)")

    # -- 2. First Muscle-up in 8 Weeks --
    def _seed_muscle_up_program(self):
        program, _ = Program.objects.update_or_create(
            name="First Muscle-up in 8 Weeks",
            defaults=dict(
                description="A structured 8-week program to build your first strict bar muscle-up. Requires at least 8 clean pull-ups and 15 dips as prerequisites.",
                target_skill=Skill.objects.filter(name="Muscle-up (Bar)").first(),
                experience_level="intermediate",
                duration_weeks=8, days_per_week=4,
            ),
        )
        self._make_workout(program, "MU -- Explosive Pull Power", 40, 1, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Band Pull-aparts", "warmup", 2, "15", 0),
            ("Active Hangs (Scapular Pull-ups)", "skill", 3, "10", 30),
            ("Chest-to-bar Pull-ups", "strength", 4, "5", 90),
            ("Explosive Pull-ups", "strength", 4, "5", 90),
            ("Straight Bar Dips", "strength", 3, "8", 90),
            ("Hanging Leg Raises", "core", 3, "10", 45),
            ("Shoulder Stretch (Cross-body)", "cooldown", 2, "30s each", 0),
        ])
        self._make_workout(program, "MU -- Transition Drills", 35, 2, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Band-assisted Muscle-ups", "skill", 5, "3", 120),
            ("Straight Bar Dips", "strength", 4, "6", 90),
            ("Negative Pull-ups", "strength", 3, "5 (slow 5s)", 90),
            ("Hollow Body Rocks", "core", 3, "15", 30),
            ("Chest Stretch (Doorway)", "cooldown", 2, "30s", 0),
        ])
        self._make_workout(program, "MU -- Pulling Strength", 40, 3, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Pull-ups", "strength", 4, "6-8", 90),
            ("Wide Grip Pull-ups", "strength", 3, "6", 90),
            ("Typewriter Pull-ups", "strength", 3, "4 each side", 90),
            ("Parallel Bar Dips", "strength", 3, "10", 60),
            ("Toes to Bar Exercise", "core", 3, "8", 45),
            ("Pike Stretch", "cooldown", 2, "30s", 0),
        ])
        self._make_workout(program, "MU -- Full Attempt Day", 35, 4, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Active Hangs (Scapular Pull-ups)", "warmup", 2, "8", 30),
            ("Bar Muscle-ups", "skill", 5, "1-3 attempts", 180),
            ("Band-assisted Muscle-ups", "skill", 3, "3", 120),
            ("Explosive Pull-ups", "accessory", 3, "5", 90),
            ("Straight Bar Dips", "accessory", 3, "6", 60),
            ("Shoulder Stretch (Cross-body)", "cooldown", 2, "30s each", 0),
        ])
        self.stdout.write("  [OK] First Muscle-up in 8 Weeks (4 workouts)")

    # -- 3. Handstand Mastery (12 weeks) --
    def _seed_handstand_program(self):
        program, _ = Program.objects.update_or_create(
            name="Handstand Mastery",
            defaults=dict(
                description="A 12-week structured program to progress from wall handstand to a confident freestanding handstand. Focuses on balance, shoulder endurance, and alignment.",
                target_skill=Skill.objects.filter(name="Freestanding Handstand").first(),
                experience_level="intermediate",
                duration_weeks=12, days_per_week=5,
            ),
        )
        self._make_workout(program, "HS -- Wall Conditioning", 25, 1, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Wrist Flexor/Extensor Stretches", "warmup", 2, "20s each", 0),
            ("Wall Handstand Holds", "skill", 5, "30-45s (chest to wall)", 60),
            ("Handstand Shoulder Taps", "skill", 3, "6 each hand", 60),
            ("Pike Push-ups", "strength", 3, "8", 60),
            ("Plank Hold", "core", 3, "45s", 30),
        ])
        self._make_workout(program, "HS -- Balance Drills", 20, 2, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Handstand Toe Pulls (Wall)", "skill", 5, "5 pull-offs, 5s each", 60),
            ("Handstand Kick-ups", "skill", 10, "1 attempt (hold max)", 30),
            ("Hollow Body Holds", "core", 3, "30s", 30),
        ])
        self._make_workout(program, "HS -- Strength Support", 30, 3, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Elevated Pike Push-ups", "strength", 4, "6", 90),
            ("Parallel Bar Dips", "strength", 3, "8", 60),
            ("Active Hangs (Scapular Pull-ups)", "strength", 3, "10", 30),
            ("Plank Hold", "core", 2, "60s", 30),
            ("Shoulder Stretch (Cross-body)", "cooldown", 2, "30s each", 0),
        ])
        self._make_workout(program, "HS -- Freestanding Practice", 20, 4, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Freestanding Handstand Hold", "skill", 10, "max hold attempts", 30),
            ("Wall Handstand Holds", "skill", 3, "30s (back to wall)", 60),
            ("Wrist Flexor/Extensor Stretches", "cooldown", 2, "20s each", 0),
        ])
        self._make_workout(program, "HS -- Active Recovery & Mobility", 20, 5, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Shoulder Dislocates (Band/Stick)", "warmup", 3, "10", 0),
            ("Crow Pose Holds", "skill", 3, "20s", 30),
            ("Bridge (Backbend)", "accessory", 3, "15s", 30),
            ("German Hang Stretch", "cooldown", 3, "15s", 0),
            ("Wrist Flexor/Extensor Stretches", "cooldown", 2, "20s each", 0),
        ])
        self.stdout.write("  [OK] Handstand Mastery (12 weeks, 5 workouts)")

    # -- 4. Front Lever Program (10 weeks) --
    def _seed_front_lever_program(self):
        program, _ = Program.objects.update_or_create(
            name="Front Lever Progression",
            defaults=dict(
                description="A 10-week program progressing from tuck front lever to full front lever. Requires 10+ pull-ups and basic hollow body as prerequisites.",
                target_skill=Skill.objects.filter(name="Full Front Lever").first(),
                experience_level="intermediate",
                duration_weeks=10, days_per_week=3,
            ),
        )
        self._make_workout(program, "FL -- Lever Holds", 35, 1, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Active Hangs (Scapular Pull-ups)", "warmup", 3, "8", 30),
            ("Tuck Front Lever Holds", "skill", 5, "10-15s", 90),
            ("Advanced Tuck FL Holds", "skill", 3, "5-8s", 90),
            ("Front Lever Negatives", "strength", 3, "3 (slow 5s)", 120),
            ("Hollow Body Holds", "core", 3, "30s", 30),
            ("Shoulder Stretch (Cross-body)", "cooldown", 2, "30s each", 0),
        ])
        self._make_workout(program, "FL -- Pulling Strength", 40, 2, [
            ("Band Pull-aparts", "warmup", 2, "15", 0),
            ("Pull-ups", "strength", 4, "6-8", 90),
            ("Australian Pull-ups (Bodyweight Rows)", "strength", 3, "12 (elevated feet)", 60),
            ("Band-assisted Front Lever", "skill", 4, "10s", 90),
            ("Hanging Leg Raises", "core", 3, "10", 45),
            ("Dragon Flags", "core", 3, "5 (negatives OK)", 60),
            ("Pike Stretch", "cooldown", 2, "30s", 0),
        ])
        self._make_workout(program, "FL -- Full Body Support", 35, 3, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Wide Grip Pull-ups", "strength", 3, "6", 90),
            ("Straddle Front Lever Holds", "skill", 4, "5-8s", 120),
            ("Parallel Bar Dips", "strength", 3, "8", 60),
            ("Toes to Bar Exercise", "core", 3, "8", 45),
            ("Skin the Cats", "accessory", 3, "5", 60),
            ("German Hang Stretch", "cooldown", 3, "15s", 0),
        ])
        self.stdout.write("  [OK] Front Lever Progression (10 weeks, 3 workouts)")

    # -- 5. Planche Progression (12 weeks) --
    def _seed_planche_program(self):
        program, _ = Program.objects.update_or_create(
            name="Planche Progression",
            defaults=dict(
                description="A 12-week program to develop tuck planche through to straddle planche. Requires 20+ push-ups and solid L-sit as prerequisites.",
                target_skill=Skill.objects.filter(name="Straddle Planche").first(),
                experience_level="advanced",
                duration_weeks=12, days_per_week=4,
            ),
        )
        self._make_workout(program, "PL -- Planche Leans & Holds", 35, 1, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Wrist Flexor/Extensor Stretches", "warmup", 2, "20s each", 0),
            ("Planche Lean Push-ups", "skill", 4, "8", 90),
            ("Tuck Planche Holds", "skill", 5, "10-15s", 90),
            ("Advanced Tuck Planche Holds", "skill", 3, "5-8s", 120),
            ("Pseudo Planche Push-ups", "strength", 3, "8", 90),
            ("Hollow Body Holds", "core", 3, "30s", 30),
        ])
        self._make_workout(program, "PL -- Pressing Strength", 40, 2, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Parallel Bar Dips", "strength", 4, "10", 60),
            ("Ring Dip Exercise", "strength", 3, "6-8", 90),
            ("Elevated Pike Push-ups", "strength", 4, "6", 90),
            ("Diamond Push-ups", "strength", 3, "12", 60),
            ("Floor L-sit Holds", "core", 3, "15-20s", 45),
            ("Pancake Stretch", "cooldown", 3, "30s", 0),
        ])
        self._make_workout(program, "PL -- Straight Arm Conditioning", 35, 3, [
            ("Wrist Circles", "warmup", 2, "10 each", 0),
            ("Band-assisted Planche", "skill", 4, "10-15s", 90),
            ("Planche Lean Push-ups", "strength", 3, "8", 90),
            ("Ring Push-ups", "strength", 3, "10", 60),
            ("V-sit Holds", "core", 3, "8-12s", 60),
            ("Straddle Stretch", "cooldown", 3, "30s", 0),
        ])
        self._make_workout(program, "PL -- Full Body", 35, 4, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Pull-ups", "strength", 3, "8", 60),
            ("Tuck Planche Holds", "skill", 3, "12-15s", 90),
            ("Parallel Bar Dips", "strength", 3, "10", 60),
            ("Hanging Leg Raises", "core", 3, "10", 45),
            ("Bodyweight Squats", "accessory", 3, "15", 60),
            ("Wrist Flexor/Extensor Stretches", "cooldown", 2, "20s each", 0),
        ])
        self.stdout.write("  [OK] Planche Progression (12 weeks, 4 workouts)")

    # -- 6. Full Body Calisthenics Strength (4 weeks) --
    def _seed_full_body_program(self):
        program, _ = Program.objects.update_or_create(
            name="Full Body Calisthenics Strength",
            defaults=dict(
                description="A 4-week full body strength program for intermediate athletes. 3 training days per week hitting push, pull, core, and legs in each session.",
                target_skill=None,
                experience_level="intermediate",
                duration_weeks=4, days_per_week=3,
            ),
        )
        self._make_workout(program, "Full Body -- Session A", 45, 1, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Leg Swings (Front-Back)", "warmup", 2, "10 each leg", 0),
            ("Pull-ups", "strength", 4, "6-8", 90),
            ("Parallel Bar Dips", "strength", 4, "8-10", 90),
            ("Bulgarian Split Squats", "strength", 3, "10 each leg", 60),
            ("Hanging Leg Raises", "core", 3, "10", 45),
            ("Plank Hold", "core", 2, "45s", 30),
            ("Pike Stretch", "cooldown", 2, "30s", 0),
        ])
        self._make_workout(program, "Full Body -- Session B", 45, 2, [
            ("Arm Circles", "warmup", 2, "10 each direction", 0),
            ("Hip Circles", "warmup", 2, "10 each direction", 0),
            ("Chin-ups", "strength", 4, "6-8", 90),
            ("Diamond Push-ups", "strength", 4, "10-12", 60),
            ("Pistol Squats", "strength", 3, "5 each leg (or Box Pistol)", 90),
            ("Dragon Flags", "core", 3, "5 (negatives OK)", 60),
            ("Side Plank Hold", "core", 2, "30s each side", 30),
            ("Figure Four Hip Stretch", "cooldown", 2, "30s each side", 0),
        ])
        self._make_workout(program, "Full Body -- Session C", 45, 3, [
            ("Inchworm", "warmup", 2, "5", 0),
            ("Band Pull-aparts", "warmup", 2, "15", 0),
            ("Archer Pull-ups", "strength", 3, "4 each side", 90),
            ("Pike Push-ups", "strength", 4, "8", 90),
            ("Nordic Curls (Eccentric)", "strength", 3, "5 (slow negatives)", 90),
            ("Toes to Bar Exercise", "core", 3, "8", 45),
            ("Hollow Body Holds", "core", 3, "30s", 30),
            ("Straddle Stretch", "cooldown", 2, "30s", 0),
        ])
        self.stdout.write("  [OK] Full Body Calisthenics Strength (4 weeks, 3 workouts)")

    # ------------------------------------------------------------------
    # ACHIEVEMENTS
    # ------------------------------------------------------------------
    def seed_achievements(self):
        achievements = [
            # Milestone achievements
            ("First Pull-up", "Complete your first strict pull-up.", "T", 50),
            ("First Muscle-up", "Land your first bar muscle-up.", "T", 200),
            ("First Handstand", "Hold a freestanding handstand for 5 seconds.", "H", 150),
            ("First Pistol Squat", "Complete a full pistol squat on each leg.", "L", 100),
            ("First L-sit", "Hold an L-sit for 5 seconds.", "S", 75),
            ("First Front Lever", "Hold a full front lever for 3 seconds.", "T", 300),
            ("First Planche", "Hold a full planche for 3 seconds.", "T", 400),

            # Verification achievements
            ("First Verified Skill", "Get your first skill verified by a moderator.", "V", 100),
            ("5 Verified Skills", "Earn verification on 5 different skills.", "V", 200),
            ("10 Verified Skills", "Earn verification on 10 different skills.", "V", 400),
            ("20 Verified Skills", "Earn verification on 20 different skills.", "V", 800),

            # Workout achievements
            ("First Workout", "Complete your first workout session.", "W", 25),
            ("10 Workouts", "Complete 10 workout sessions.", "W", 100),
            ("50 Workouts", "Complete 50 workout sessions.", "W", 300),
            ("100 Workouts", "Complete 100 workout sessions. Ironclad consistency!", "W", 500),

            # Streak achievements
            ("7-Day Streak", "Train 7 days in a row.", "F", 50),
            ("30-Day Streak", "Train 30 days in a row. A full month of dedication.", "F", 150),
            ("100-Day Streak", "Train 100 days in a row. Legendary commitment.", "F", 500),

            # Category mastery
            ("Push Master", "Verify all push skills up to advanced level.", "P", 300),
            ("Pull Master", "Verify all pull skills up to advanced level.", "P", 300),
            ("Core Master", "Verify all core skills up to advanced level.", "C", 300),
            ("Leg Master", "Verify all leg skills up to advanced level.", "L", 300),
            ("Balance Master", "Verify all balance skills up to advanced level.", "B", 300),

            # Program achievements
            ("Program Graduate", "Complete your first full training program.", "G", 300),
            ("3 Programs Completed", "Complete 3 different training programs.", "G", 500),

            # Elite achievements
            ("Elite Athlete", "Reach the Elite rank.", "E", 1000),
            ("Iron Cross Holder", "Achieve a verified Iron Cross.", "X", 500),
            ("One-arm Wonder", "Achieve a verified one-arm pull-up.", "D", 500),
            ("Gravity Defier", "Verify both Full Front Lever and Full Planche.", "R", 1000),
        ]
        for name, desc, icon, xp in achievements:
            Achievement.objects.update_or_create(
                name=name, defaults={"description": desc, "icon": icon, "xp_reward": xp}
            )
        self.stdout.write("  [OK] %d achievements" % len(achievements))
