from django.db import models
from django.conf import settings
from skills.models import Skill


class Exercise(models.Model):
    """Reusable exercise library block used inside workouts (section 36)."""
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    related_skill = models.ForeignKey(
        Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="exercises"
    )

    def __str__(self):
        return self.name

    def get_motion_type(self):
        """Map exercise to biomechanical animation archetype for interactive visualizer."""
        n = self.name.lower()
        if 'diamond push' in n: return 'diamond_pushup'
        if 'pike push' in n: return 'pike_pushup'
        if 'decline push' in n: return 'decline_pushup'
        if 'archer push' in n: return 'archer_pushup'
        if 'pseudo planche' in n or 'planche lean' in n: return 'planche'
        if 'handstand push' in n or 'hspu' in n: return 'hspu'
        if 'push-up' in n or 'pushup' in n or 'push up' in n: return 'pushup'
        if 'muscle-up' in n or 'muscle up' in n: return 'muscleup'
        if 'chin-up' in n or 'chin up' in n: return 'chinup'
        if 'scapular pull' in n or 'active hang' in n: return 'scapular_pull'
        if 'dead hang' in n or 'hang' in n: return 'dead_hang'
        if 'australian' in n or 'row' in n: return 'australian_row'
        if 'pull-up' in n or 'pullup' in n or 'pull up' in n: return 'pullup'
        if 'dip' in n: return 'dips'
        if 'pistol' in n or 'shrimp' in n: return 'pistol_squat'
        if 'bulgarian' in n or 'lunge' in n or 'step-up' in n: return 'lunge'
        if 'squat' in n or 'wall sit' in n: return 'squat'
        if 'calf' in n: return 'calf_raise'
        if 'nordic' in n or 'leg extension' in n: return 'nordic_curl'
        if 'glute' in n or 'bridge' in n: return 'glute_bridge'
        if 'front lever' in n or 'fl hold' in n: return 'front_lever'
        if 'back lever' in n: return 'back_lever'
        if 'planche' in n: return 'planche'
        if 'handstand' in n or 'headstand' in n: return 'handstand'
        if 'crow' in n or 'elbow lever' in n: return 'crow_pose'
        if 'l-sit' in n or 'lsit' in n or 'v-sit' in n: return 'lsit'
        if 'dragon flag' in n: return 'dragon_flag'
        if 'leg raise' in n or 'knee raise' in n or 'toes to bar' in n or 'windshield' in n or 'bicycle' in n or 'climber' in n: return 'hanging_leg_raise'
        if 'hollow' in n or 'dead bug' in n: return 'hollow_body'
        if 'side plank' in n: return 'side_plank'
        if 'plank' in n or 'ab wheel' in n or 'pallof' in n: return 'plank'
        if 'stretch' in n or 'circle' in n or 'inchworm' in n or 'dislocate' in n or 'swing' in n: return 'mobility'
        return 'pushup'

    def get_embed_url(self):
        """Convert standard YouTube links to responsive embed URLs."""
        url = self.video_url
        if not url and self.related_skill and self.related_skill.tutorial_video_url:
            url = self.related_skill.tutorial_video_url
        if not url:
            return ""
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtube.com/embed/" in url:
            return url
        return url

    def get_target_muscles(self):
        """Return target muscle tags for UI badges."""
        if self.related_skill and self.related_skill.muscle_groups:
            return [m.strip() for m in self.related_skill.muscle_groups.split(",") if m.strip()]
        m_type = self.get_motion_type()
        muscle_map = {
            'pushup': ['Chest', 'Triceps', 'Anterior Delts', 'Core'],
            'diamond_pushup': ['Triceps (Inner Head)', 'Chest', 'Core'],
            'pike_pushup': ['Shoulders (Delts)', 'Triceps', 'Upper Traps'],
            'decline_pushup': ['Upper Chest', 'Deltoids', 'Triceps'],
            'archer_pushup': ['Chest', 'Triceps', 'Core Stability'],
            'dips': ['Chest', 'Triceps', 'Anterior Deltoids'],
            'hspu': ['Deltoids', 'Triceps', 'Trapezius', 'Core'],
            'pullup': ['Lats', 'Biceps', 'Rhomboids', 'Grip'],
            'chinup': ['Biceps', 'Lats', 'Upper Back'],
            'australian_row': ['Rhomboids', 'Rear Delts', 'Lats', 'Biceps'],
            'scapular_pull': ['Lower Traps', 'Rhomboids', 'Forearms'],
            'dead_hang': ['Forearms / Grip', 'Scapular Stabilizers', 'Lats'],
            'muscleup': ['Lats', 'Chest', 'Triceps', 'Explosive Pull'],
            'squat': ['Quadriceps', 'Glutes', 'Hamstrings', 'Calves'],
            'pistol_squat': ['Quadriceps', 'Glutes', 'Ankle Stabilizers', 'Core'],
            'lunge': ['Quadriceps', 'Glutes', 'Hamstrings'],
            'calf_raise': ['Gastrocnemius', 'Soleus', 'Achilles'],
            'nordic_curl': ['Hamstrings', 'Glutes', 'Calves'],
            'glute_bridge': ['Glutes', 'Hamstrings', 'Lower Back'],
            'plank': ['Rectus Abdominis', 'Transverse Abdominis', 'Shoulders'],
            'side_plank': ['Obliques', 'Quadratus Lumborum', 'Glute Medius'],
            'lsit': ['Hip Flexors', 'Rectus Abdominis', 'Triceps', 'Shoulders'],
            'hanging_leg_raise': ['Lower Abs', 'Hip Flexors', 'Grip'],
            'dragon_flag': ['Entire Abdominal Wall', 'Lats', 'Hip Flexors'],
            'hollow_body': ['Rectus Abdominis', 'Hip Flexors', 'Spinal Bracers'],
            'handstand': ['Deltoids', 'Trapezius', 'Wrists', 'Core Balance'],
            'crow_pose': ['Wrists', 'Anterior Delts', 'Core'],
            'planche': ['Anterior Deltoids', 'Biceps Tendons', 'Upper Chest', 'Core'],
            'front_lever': ['Lats', 'Rear Delts', 'Core', 'Teres Major'],
            'back_lever': ['Biceps Tendons', 'Chest', 'Posterior Chain'],
            'mobility': ['Joint Mobility', 'Rotator Cuff', 'Flexibility'],
        }
        return muscle_map.get(m_type, ['Full Body', 'Core'])

    def get_form_cues(self):
        """Return 3 golden coaching cues for performing the exercise."""
        if self.related_skill and self.related_skill.technique_instructions:
            lines = [line.strip() for line in self.related_skill.technique_instructions.split('\n') if line.strip()]
            if lines:
                return lines[:3]
        m_type = self.get_motion_type()
        cues_map = {
            'pushup': [
                'Keep elbows tucked at a 45-degree angle to protect shoulders.',
                'Squeeze glutes and core to keep body in a rigid straight plank line.',
                'Lower until chest touches the floor, then press to full arm lockout.'
            ],
            'diamond_pushup': [
                'Form a diamond with index fingers and thumbs under mid-chest.',
                'Keep elbows close to your torso during the entire descent.',
                'Focus on flexing triceps at the peak lockout.'
            ],
            'pike_pushup': [
                'Hike hips high in an inverted V shape with straight legs and back.',
                'Lower head forward forming a triangle with your hands.',
                'Press up and push head back through your arms at top.'
            ],
            'dips': [
                'Depress shoulders downwards and lean torso slightly forward.',
                'Lower until elbows reach at least a 90-degree angle.',
                'Push up explosively and lock out elbows with full control.'
            ],
            'pullup': [
                'Initiate every pull by depressing scapulae (pull shoulders down).',
                'Drive elbows down towards hips to fully engage lats.',
                'Pull chest over the bar and lower down to a complete dead hang.'
            ],
            'chinup': [
                'Supinated grip (palms facing you) shoulder-width apart.',
                'Lead with chest up toward the bar, driving elbows back.',
                'Control the negative descent all the way to straight arms.'
            ],
            'muscleup': [
                'Generate explosive vertical chest-to-bar pulling power.',
                'Aggressively whip head and chest forward over the bar in transition.',
                'Press out the top straight bar dip to full arm lockout.'
            ],
            'squat': [
                'Keep chest proud and drive knees outward tracking in line with toes.',
                'Descend until thighs break parallel with the ground.',
                'Drive firmly through heels and mid-foot to stand tall.'
            ],
            'pistol_squat': [
                'Extend non-working leg forward with toes pointed upward.',
                'Keep working foot flat on floor without heel lifting.',
                'Descend smoothly with control, then drive through heel to stand.'
            ],
            'plank': [
                'Tuck pelvis into posterior pelvic tilt (hollow body posture).',
                'Push ground away through forearms to protract shoulder blades.',
                'Breathe rhythmically while maintaining constant abdominal tension.'
            ],
            'lsit': [
                'Depress shoulders aggressively into the floor or bars.',
                'Lock knees completely and point toes with quads flexed.',
                'Compress abs and pull hips slightly back between hands.'
            ],
            'hanging_leg_raise': [
                'Start from a dead hang with zero swinging momentum.',
                'Curl pelvis upward toward ribcage as legs rise.',
                'Control the descent back down; do not let legs drop passively.'
            ],
            'handstand': [
                'Push tall through shoulders (elevation) to lock the shoulder girdle.',
                'Grip floor with fingertips like claws for micro-balance adjustments.',
                'Keep ribs tucked and legs squeezed tightly together in a straight line.'
            ],
            'front_lever': [
                'Retract and pull shoulders down toward hips with straight arms.',
                'Maintain a rigid hollow body without allowing hips to sag or pike.',
                'Pull down on the bar continuously as if performing a straight-arm pulldown.'
            ],
            'planche': [
                'Lean shoulders forward well ahead of wrists with straight locked arms.',
                'Protract scapulae maximally into an upper back dome.',
                'Squeeze glutes, point toes, and clamp core in complete hollow tension.'
            ],
        }
        return cues_map.get(m_type, [
            'Maintain strict form throughout the full range of motion.',
            'Control the eccentric (lowering) phase for 2 to 3 seconds.',
            'Breathe consistently and avoid using swinging momentum.'
        ])


class Program(models.Model):
    """A multi-week training program, e.g. '8-week First Muscle-up' (section 12)."""
    GOAL_SKILL = "skill"

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    target_skill = models.ForeignKey(
        Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="programs"
    )
    experience_level = models.CharField(max_length=20, blank=True)
    duration_weeks = models.PositiveIntegerField(default=4)
    days_per_week = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.name


class Workout(models.Model):
    """A single workout template (section 13)."""
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="workouts", null=True, blank=True
    )
    title = models.CharField(max_length=150)
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    order_in_program = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["program", "order_in_program"]

    def __str__(self):
        return self.title


class WorkoutExercise(models.Model):
    """Sets/reps prescription for an exercise inside a workout."""
    SECTION_CHOICES = [
        ("warmup", "Warm-up"),
        ("skill", "Skill / Technique"),
        ("strength", "Strength"),
        ("accessory", "Accessory"),
        ("core", "Core / Conditioning"),
        ("cooldown", "Cool down"),
    ]

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="workout_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default="strength")
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=50, help_text="e.g. '10' or '30s hold'")
    rest_seconds = models.PositiveIntegerField(default=60)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "order"]

    def __str__(self):
        return f"{self.workout} - {self.exercise}"


class WorkoutSession(models.Model):
    """A user's attempt at a workout (section 14)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_sessions"
    )
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.workout} ({self.started_at:%Y-%m-%d})"


class ExerciseLog(models.Model):
    """Actual sets/reps performed during a session, feeding the progression system (section 15)."""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name="exercise_logs")
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE)
    sets_completed = models.PositiveIntegerField(default=0)
    reps_completed = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.session} - {self.workout_exercise.exercise}"


class Challenge(models.Model):
    """Calisthenics bounties, daily & weekly challenges (spec sections 22/37)."""
    CADENCE_CHOICES = [
        ("daily", "Daily Challenge"),
        ("weekly", "Weekly Bounty"),
        ("special", "Milestone Challenge"),
    ]
    CATEGORY_CHOICES = [
        ("push", "Push Power"),
        ("pull", "Pull Strength"),
        ("core", "Iron Core"),
        ("legs", "Legs & Explosiveness"),
        ("skill", "Static & Skill"),
        ("endurance", "Work Capacity"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="push")
    cadence = models.CharField(max_length=20, choices=CADENCE_CHOICES, default="daily")
    target_metric = models.CharField(max_length=50, help_text="e.g. '100 push-ups' or '3 min plank'")
    target_value = models.PositiveIntegerField(default=100)
    xp_reward = models.PositiveIntegerField(default=75)
    badge_icon = models.CharField(max_length=10, default="🎯")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cadence", "-xp_reward"]

    def __str__(self):
        return f"[{self.get_cadence_display()}] {self.title} (+{self.xp_reward}XP)"


class UserChallenge(models.Model):
    """Tracks athlete completion/progress on challenges."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_challenges"
    )
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="user_records")
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    xp_claimed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "challenge")

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.progress}/{self.challenge.target_value})"

