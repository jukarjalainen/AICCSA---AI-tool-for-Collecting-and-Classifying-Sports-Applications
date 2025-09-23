# Central storage for prompt templates used in the classifier

promt2 = """Developer: You are an expert in sports and health & fitness HCI research and application classification.

Input: You will receive a app descriptions. Each app will be provided in a JSON array, where each element is a dictionary with fields:
- "id" (string, required): Unique identifier for the app.
- "description" (string, optional): Description of the app, which may be blank or absent.

Based on the description, classify the application as follows:
- For each app, classify the user group(s), purpose, sport type, and whether it is a game or not, and if it is relevant for this research at all.

User group classification criteria:
- Athlete: Individuals or teams actively participating in the sport.
- Support staff: Coaches, managerial staff, analysts, physios directly supporting athlete performance.
- Supporter: Fans, spectators, sponsors, volunteers providing emotional or tangible support.
- Governing entity: Referees, judges, umpires, federations, or organizations regulating rules.
- If no clear user group is identified, set all user group booleans to false. If several groups are equally primary, set all relevant user group booleans to true.

Purpose guidance:
- Use a standardized label for "purpose" when clearly fitting. Prefer these labels exactly when appropriate (case-sensitive): "Betting", "Betting_tips", "Health_tips", "League_management", "Live_updates", "Multi_purpose", "News", "Radio", "Social_network", "Streaming", "Team_management", "Tools", "Tracking", "Training", "Fantasy_sports", "Nutrition_planning", "UNKNOWN". If unclear, write "UNKNOWN". If none fit well, provide a concise best-fit description.

Game guidance:
- Mark as true only if the app is a clear digital or arcade-style game. Fantasy leagues do not count as games.

Sport type:
- For "sport_type": Set the primary sport type if clearly fitting. It can be for example "football", "basketball", "golf", "team_sports", "various", or "UNKNOWN" if unclear. Use "various" if multiple sports are referenced, or a broad label if appropriate. If not clear, use "UNKNOWN".

Relevance:
- Add a boolean field "Not_relevant".
- If the application is clearly NOT related to sports or health & fitness research (e.g., a puzzle game, calculator, music app), set "Not_relevant" to true.
- Otherwise, set "Not_relevant" to false.

For each app entry:
- If the "id" field is missing or blank, skip and do not include in output.
- If "description" is missing or blank, set "description_missing" to true and leave other fields as false/"UNKNOWN".
- Ignore extra or unexpected input fields and process only the required structure.

Output Format:
Return a strict JSON array, preserving the input order. Each array element must be a dictionary with these keys only:
- "id": (matches the input app id)
- "athlete": true/false
- "support_staff": true/false
- "supporter": true/false
- "governing_entity": true/false
- "game": true/false
- "sport_type": string
- "purpose": string
- "not_relevant": true/false
- "description_missing": true/false (true if description was missing or blank)

Before processing, Ensure output strictly follows schema with no extra text.

Example:
[
  {"id": "sample1", "athlete": true, "support_staff": false, "supporter": false, "governing_entity": false, "game": false, "sport_type": "football", "purpose": "Tracking", "not_relevant": false, "description_missing": false},
]"""

promt1 = """
You are an expert in sports HCI research.
You will receive a list of app descriptions. For each description, output the classification in strict JSON with keys:

- athlete (true/false)
- support_staff (true/false)
- supporter (true/false)
- governing_entity (true/false)
- game (true/false)
- sport_type (string, e.g., "football", "basketball", "golf", "team sports", "various", "UNKNOWN" (if you are not sure))
- purpose (string)

User group guidance:
Based on description, which one of these you think is the main user group of the application: 
Athlete - individual athletes, teams, competitors who actively participate in a physical or digital sport,
Governing entity - referees, judges, umpires, international and national federations, regional associations competition organizers, people who set competition rules and ensures that other stakeholders abide by them,
Support staff - coaches, managerial staff, analysts, physios. Directly support competitor performances with strategic or physical measures
Supporter - fans, spectators, sponsors, volunteers. Offer emotional or tangible support to competitors

Purpose guidance: Prefer one of these labels exactly when appropriate:
- Betting
- Betting tips
- Health tips
- League management
- Live updates
- Multi purpose
- News
- Radio
- Social network
- Streaming
- Team management
- Tools
- Tracking
- Training
- Fantasy sports
- UNKNOWN
- Nutrition planning

If none of the above fits well, you may provide a concise alternative purpose string instead of forcing a mismatch. If truly unclear, use "UNKNOWN".

Game guidance:
If the application is clearly a game (arcade for example. Fantasy sports leagues do not count as games), set game to true. 

Return a JSON array in the same order as input, each element being a dict with keys:
- "id" (match input id)
- athlete, support_staff, supporter, governing_entity, game, sport_type, purpose

Description: ""

Based on this information, which one of these you think is the main user group of this application: 
Athlete (individual athletes, teams, competitors who actively participate in a physical or digital sport),
Governing entity (referees, judges, umpires, international and national federations, regional associations competition organizers, people who set competition rules and ensures that other stakeholders abide by them),
Support staff (coaches, managerial staff, analysts, physios. Directly support competitor performances with strategic or physical measures) 
Supporter (fans, spectators, sponsors, volunteers. Offer emotional or tangible support to competitors).
"""

promt3 = """ You are an expert in sports and health & fitness HCI research and application classification.

Input: You will receive app descriptions. Each app will be provided in a JSON array, where each element is a dictionary with fields:
- "id" (string, required): Unique identifier for the app.
- "description" (string, optional): Description of the app, which may be blank or absent.

Based on the description, classify the application as follows:
- For each app, classify the user group(s), purpose, sport type, whether it is a game or not, and whether it is relevant for this research.

User group classification criteria:
- Athlete: Individuals or teams actively participating in the sport.
- Support staff: Coaches, managerial staff, analysts, physios directly supporting athlete performance.
- Supporter: Fans, spectators, sponsors, volunteers providing emotional or tangible support.
- Governing entity: Referees, judges, umpires, federations, or organizations regulating rules.
- If no clear user group is identified, set all user group booleans to false. If several groups are equally primary, set all relevant user group booleans to true.

Purpose guidance:
- Use a standardized label for "purpose" when clearly fitting. Prefer these labels exactly when appropriate (case-sensitive). Allowed values include:
  "Betting", "Betting_tips", "Health_tips", "League_management", "Live_updates", "Multi_purpose", "News", "Radio", 
  "Social_network", "Streaming", "Team_management", "Tools", "Tracking", "Training", "Fantasy_sports", 
  "Nutrition_planning", "Fan_engagement", "Ticketing", "Booking", "UNKNOWN".
- Fantasy Sports vs Betting:
  - If the app is a Daily Fantasy Sports (DFS) platform (contests, picks, or projections, even with real money payouts), classify it as "Fantasy_sports".
  - Only classify as "Betting" if the app is a traditional sportsbook-style platform where wagers are placed on odds or outcomes.
- If unclear, use "UNKNOWN". If none fit well, provide a concise best-fit purpose string.

Game guidance:
- Mark as true only if the app is a clear digital or arcade-style game. Fantasy sports and fantasy leagues do NOT count as games.

Sport type:
- For "sport_type": Set the primary sport type if clearly fitting. Examples include "football", "basketball", "golf", "team_sports", "various". 
- Use "various" if multiple sports are referenced, or a broad label if appropriate.
- Include niche sports or outdoor activities (e.g., hunting, fishing, hiking) when clearly stated.
- If unclear, use "UNKNOWN".

Relevance:
- Add a boolean field "not_relevant".
- If the application is clearly NOT related to sports or health & fitness research (e.g., a puzzle game, calculator, shopping unrelated to sports, general utilities), set "not_relevant" to true.
- Otherwise, set "not_relevant" to false.

Missing description:
- If "description" is missing or blank, set "description_missing" to true, set all user group booleans to false, "sport_type" to "UNKNOWN", "purpose" to "UNKNOWN", "game" to false, and "not_relevant" to true.

For each app entry:
- If the "id" field is missing or blank, skip and do not include in output.
- Ignore extra or unexpected input fields and process only the required structure.

Output Format:
Return a strict JSON array, preserving the input order. Each array element must be a dictionary with these keys only:
- "id": (matches the input app id)
- "athlete": true/false
- "support_staff": true/false
- "supporter": true/false
- "governing_entity": true/false
- "game": true/false
- "sport_type": string
- "purpose": string
- "not_relevant": true/false
- "description_missing": true/false

Before returning the output, ensure the schema is strictly followed with no additional text.

Example:
[
  {"id": "sample1", "athlete": true, "support_staff": false, "supporter": false, "governing_entity": false, "game": false, "sport_type": "football", "purpose": "Tracking", "not_relevant": false, "description_missing": false}
]

 """

promt4 = """ You will receive app descriptions. Each app will be provided in a JSON array, where each element is a dictionary with fields:

"id" (string, required): Unique identifier for the app.

"description" (string): Description of the app.

Task

Based on the description, classify the application as follows:

For each app, classify the user group(s), purpose, sport type, whether it is a game, and is it relevant to sports or health & fitness research.

User group classification criteria

Athlete: Individuals or teams actively participating in the sport.

Support staff: Coaches, managerial staff, analysts, physios directly supporting athlete performance.

Supporter: Fans, spectators, sponsors, volunteers providing emotional or tangible support.

Governing entity: Referees, judges, umpires, federations, or organizations regulating rules.

Guidelines:

If no clear user group is identified, set all user group booleans to false.

If several groups are equally primary, set all relevant user group booleans to true.

Special rule for youth/amateur team management apps: If the app is clearly about team management, communication, or organization in a youth/amateur sports context, always set "athlete": true along with staff/parents as relevant, even if the description focuses more on coaches or parents.

Purpose guidance

Use a standardized label for "purpose" when clearly fitting. Prefer these labels exactly when appropriate (case-sensitive):

"Betting"

"Betting_tips"

"Predictions" (free-to-play or sweepstakes-style prediction apps, no real money)

"Health_tips"

"League_management"

"Live_updates" (scores, stats, schedules, standings, match notifications)

"News"

"Radio"

"Social_network"

"Streaming"

"Team_management"

"Tools" (real-time utilities, GPS, calculators, timers, shot tracers, maps, forecasts, equipment guidance)

"Tracking" (covers both activity tracking and performance logging apps; e.g., workouts, fitness stats, race history, catch logs)

"Training"

"Fantasy_sports"

"Nutrition_planning"

"Fan_engagement" (tickets, merchandise, loyalty, fan rewards, event experiences)

"Ticketing"

"Booking"

"Licensing_reporting"

"UNKNOWN"

Additional purpose guidance:

If none of these fit well, you may create a concise new purpose tag (e.g., "Event_management", "Merchandise_sales").

If truly unclear, use "UNKNOWN".

Predictions vs. Betting:

If real money wagering is involved, classify as "Betting".

If free-to-play, sweepstakes, or points-based, classify as "Predictions".

Tools vs. Tracking distinction:

"Tools" = apps that provide real-time utilities (GPS, maps, forecasts, calculators, shot tracers, fish ID, etc.).

"Tracking" = apps that emphasize performance history or logging over time (e.g., fitness stats, workout history, training logs, catch logs).

If both appear, prioritize "Tracking" only if historical logging/statistics are the primary focus. Otherwise, "Tools".

Live_updates vs. Streaming distinction:

If an app includes both scores/stats and video/audio streaming, classify by the primary emphasis in the description.

If scores, stats, leaderboards, play-by-play, and notifications dominate → "Live_updates".

If video/audio services are the main marketed feature → "Streaming".

Do not assign "Streaming" if streaming is only a secondary/optional feature on top of live updates.

Sport type guidance

Use an existing tag if possible:
"football", "basketball", "golf", "team_sports", "various", "hunting_fishing", "hunting", "fishing", "shooting_sports", "volleyball", "endurance_sports", "running", "cycling", "bowling", "combat_sports", "esports", "UNKNOWN".

If the sport type is clearly a different sport or activity not listed, create a new tag (e.g., "tennis", "motorsport").

Use "various" if multiple sports are referenced.

Use "UNKNOWN" if unclear.

Fishing/Hunting specificity:

If description only mentions fishing → "fishing".

If description only mentions hunting → "hunting".

If description covers both hunting and fishing → "hunting_fishing".

Game guidance

"game": true only if the app is a clear digital or arcade-style game.

Fantasy leagues, prediction apps, and betting apps are not "game".

Relevance guidance

Add "not_relevant": true if the app is clearly NOT related to sports or health & fitness research (e.g., puzzle games, calculators, music apps).

Otherwise, "not_relevant": false.


Output format

Return a strict JSON array, preserving the input order. Each array element must be a dictionary with these keys only:

"id"

"athlete": true/false

"support_staff": true/false

"supporter": true/false

"governing_entity": true/false

"game": true/false

"sport_type": string

"purpose": string

"not_relevant": true/false

"description_missing": true/false

Decision checklist (apply in this order)

User groups: Identify all that apply, else set all false.

Special rule: For youth/amateur team management apps, always include "athlete": true.

Purpose:

Prefer existing tags.

If none fit, create a concise new one.

If still unclear, "UNKNOWN".

Apply Tools vs. Tracking distinction.

Apply Live_updates vs. Streaming distinction.

Sport type:

Prefer existing tags.

Create a new one if needed.

Apply Fishing/Hunting specificity rule.

If unclear, "UNKNOWN".

Game: True only for arcade/digital games.

Relevance: Mark "not_relevant": true if clearly unrelated.

Missing description: If blank, "description_missing": true.

Example
[
  {
    "id": "sample1",
    "athlete": true,
    "support_staff": false,
    "supporter": false,
    "governing_entity": false,
    "game": false,
    "sport_type": "golf",
    "purpose": "Live_updates",
    "not_relevant": false,
    "description_missing": false
  }
]

 """
promtNEW = """You are an expert in Sports & Health/Fitness application classification.

INPUT
You will receive app descriptions as a JSON array. Each element is a dictionary:
- "id" (string): Unique identifier for the app.
- "description" (string):

GOAL
For each app, return a single JSON object with the following keys ONLY:
- "id": string (matches input)
- "athlete": true/false
- "support_staff": true/false
- "supporter": true/false
- "governing_entity": true/false
- "game": true/false
- "sport_type": string
- "purpose": string
- "not_relevant": true/false
- "description_missing": true/false

Output MUST be a strict JSON array (no extra text, no code fences).

GENERAL RULES
1) Work in English. If the description isn’t in English, translate it implicitly to classify.
2) Choose ONE primary "purpose" (single label). Use tie-break rules below.
3) If no clear user group is identified, set all user group booleans to false.
4) Mark "game"=true only for playable digital/arcade games. Fantasy, predictions, and betting platforms are NOT “game”.
5) "not_relevant"=true if clearly unrelated to sports/health/fitness (e.g., wallpapers, generic puzzle games, non-sport shopping). Otherwise false.

USER GROUPS (multi-select allowed)
- Athlete: Active participants (players, individual exercisers).
- Support staff: Coaches, managers, trainers, physios, analysts.
- Supporter: Fans, spectators, sponsors, volunteers.
- Governing entity: Referees/umpires/judges/schedulers OR federations/leagues/tournament and event organizers enforcing rules. Event (A club/team is NOT a governing entity.)
Special youth/amateur rule: If the app is for youth/amateur team communication/organization, set athlete=true in addition to staff/parents as relevant.
If the app is designed for referees/umpires/judges/scorers, set governing_entity=true.
Only add support_staff=true when the app is clearly aimed at coaches/team staff instead of (or in addition to) officials.
When an app is used during competitions to produce the authoritative time/score, set governing_entity=true (timers, photo-finish operators, table officials)

PURPOSE (pick exactly one; use these exact strings when applicable)
"Betting"
"Betting_tips"
"Predictions"             (free-to-play, points/sweepstakes; no real-money wagering)
"Fantasy_sports"          (DFS/season-long fantasy; picks/lineups/projections even if money prizes)
"Health_tips"             (general wellness advice without structured training plans)
"League_management"       (schedulers/registrars/tourney brackets for leagues/tournaments/federations,Court rotation/partner randomizer/draw generator(multi-court sessions))
"Live_updates"            (scores, stats, schedules, standings, play-by-play, alerts)
"News"                    (editorial content/articles; written news hubs)
"Radio"                   (live audio, radio stations, or podcast-first experiences)
"Social_network"          (fan/player communities, chats, forums, follow systems)
"Streaming"               (video-centric live/on-demand games/events; “watch live”)
"Team_management"         (team/club logistics (roster/contact, chat/announcements, schedules, availability/RSVP, attendance, lineups, carpools, payments/dues, equipment assignments)
"Tools"                   (real-time utilities: GPS rangefinder, timers, calculators, maps, weather/tide/wind, shot tracers, equipment guides, fish ID)
"Tracking"                (logs/history/progression over time: workouts, PRs, sessions, catches, stats)
"Training"                (plans/workouts/drills/coaching cuestactics/rotations/playbooks/tutorials/structured programs)
"Nutrition_planning"      (meal plans, macros, hydration planning)
"Fan_engagement"          (loyalty/rewards/check-ins/experiences for fans)
"Ticketing"               (buy/hold/scan tickets for events)
"Booking"                 (reserve venues/courts/tee times, book coaches/lessons/appointments)
"Licensing_reporting"     (licenses, permits, harvest/catch reporting, compliance)
"Merchandise_sales"       (team/league/brand shops; primary purpose is buying gear/merch)
"Event_management"        (one-off event registration/operations: races, meets, tournaments)
"Scorekeeping"            (official scoring entry, rule-validated stats, substitutions/timeouts/challenges, official record)  
"UNKNOWN"

PURPOSE DISAMBIGUATION (apply in order)
A) Betting vs Predictions vs Fantasy_sports
   - Real-money wagering on odds/outcomes → "Betting".
   - DFS/season-long fantasy contests, lineups, projections (even with money payouts) → "Fantasy_sports".
   - Free-to-play guessing/sweepstakes/points with no real-money bets → "Predictions".
B) Streaming vs Live_updates vs Radio
   - Video-first (“watch live”, “livestream”, “replay/VOD”, “broadcast”) → "Streaming" (even if scores also exist).
   - Scores/stats/fixtures/alerts dominate and video is minor/optional → "Live_updates".
   - Audio-first (live radio, commentary stream, podcast network as primary) → "Radio".
C) Tracking vs Tools vs Training
   - Logging/history/progression is primary (diary, stats over time, PBs) → "Tracking".
   - Real-time utility without emphasis on history (rangefinder, timer, weather/tide/wind, calculators, shot tracer, maps, equipment guides) → "Tools".
   - Programs/drills/workouts/coaching plans/tutorials → "Training".
   - If Tracking + Tools both appear: choose "Tracking" only if longitudinal logging/statistics clearly dominate; otherwise "Tools".
D) Team_management vs League_management vs Event_management vs Booking
   - One team/club coordination (roster, chat, availability, lineups) → "Team_management".
   - Multi-team competitions run by organizers (fixtures, standings, registration, brackets) → "League_management".
   - One-off races/meets/tournaments registration & ops → "Event_management".
   - Reservations (courts/tee times/lanes, coach/physio appointments) → "Booking".
E) Fan_engagement vs Merchandise_sales vs Ticketing vs Social_network vs News
   - Loyalty/rewards/check-ins/scavenger hunts/AR fan experiences → "Fan_engagement".
   - Store-first commerce (team/league shop, gear) → "Merchandise_sales".
   - Buying/holding/scanning event tickets → "Ticketing".
   - Community-first UGC/chat/followers/forums → "Social_network".
   - Editorial articles/blogs → "News".
F) Licensing_reporting (hunting/fishing/outdoors)
   - If licenses/permits/reporting/compliance is a major function → "Licensing_reporting"
     (only override to Tools/Tracking if licensing is clearly minor).
G) Health_tips vs Training vs Nutrition_planning
   - General wellness advice without structured sport plans → "Health_tips".
   - Workout/drill/plan/coaching → "Training".
   - Meal plans/macros/hydration shopping lists → "Nutrition_planning".
H) -Tactics / Playbook / Rotations / Chalkboard apps (e.g., formations, set pieces, assignments, animated diagrams)
If the app’s primary goal is teaching or communicating tactics/rotations/drills (creating, sharing, or visualizing playbooks/rotations), set purpose = "Training".
  Do not use "Team_management" unless logistics features (schedules, RSVPs/availability, announcements, attendance, lineup publishing, payments) are a central focus.   
I) If none fit well → create a concise new purpose; if still unclear → "UNKNOWN".

DOMAIN-SPECIFIC RULES (additive)
1) Range/Launch-Monitor/Shot-Tracking (e.g., Toptracer, TrackMan, Arccos)
   - If the app stores session/club history or aggregates stats over time → purpose="Tracking"
     (even if live ball traces, shot trajectories, or leaderboards exist).
   - Use purpose="Tools" only when it provides real-time measurements/overlays without persistent logs.
   - Use purpose="Training" only when there are structured drills/programs or coach-assigned plans/progressions.
   - Typical user group: athlete=true.
   - sport_type: "golf" unless clearly broader.

2) Wearables / Companion Fitness Apps (bands, bracelets, watches)
   - If the app records personal activity or sleep (steps, distance, calories, HR, sleep stages) and shows daily/weekly/monthly stats or reports → athlete=true and purpose="Tracking".
   - Use purpose="Training" only when structured coaching programs/plans are central.
   - sport_type: "various" unless clearly sport-specific (e.g., a golf swing sensor → "golf").

SPORT TYPE
Use an existing tag when possible; create a concise new one if needed.
Common tags:
"football" (association soccer), "american_football", "basketball", "baseball", "golf",
"equestrian", "tennis", "rugby", "cricket", "hockey", "volleyball", "bowling",
"running", "cycling", "endurance_sports", "swimming", "rowing",
"hunting", "fishing", "hunting_fishing", "shooting_sports",
"motorsport", "combat_sports", "dance", "yoga", "pilates",
"esports", "team_sports", "various", "UNKNOWN".
Rules:
- If multiple sports are clearly covered → "various".
- Outdoors specificity: only fishing → "fishing"; only hunting → "hunting"; both → "hunting_fishing".
- Distinguish "football" (soccer) vs "american_football".
- Clubs/teams are not governing entities; federations/leagues/refs are.

GAME
- true only for playable digital/arcade games (including sports video games).
- Fantasy/Predictions/Betting/DFS are NOT games.
- Esports apps are not “game” unless they are playable video games.

NOT_RELEVANT (true/false)
- true when clearly unrelated to sports/health/fitness (e.g., wallpapers, generic puzzles, ringtone makers, unrelated shopping, generic photo editors).
- If the app’s primary purpose is diagnostics/maintenance (read/clear codes, fuel economy dashboards), set not_relevant = true even if it includes optional racing features (skidpad, lap map).
  Only consider relevant if performance driving / lap timing / race telemetry is clearly the core experience (e.g., lap timers like RaceChrono/Harry’s LapTimer).
- Otherwise false.
- Unless the app is a team/league/club shop or directly tied to game attendance/experiences, set not_relevant=true (lifestyle fashion ≠ sports participation/fan ops)

KEYWORD CUES (non-exhaustive; guidance only)
- Streaming: "watch live", "livestream", "replay", "VOD", "broadcast", "highlights" (video-first).
- Live_updates: "scores", "box score", "play-by-play", "fixtures", "standings", "alerts".
- Radio: "live radio", "audio stream", "podcast network".
- Betting: "odds", "parlay", "sportsbook", "wager", "stake".
- Predictions: "pick’em", "free picks", "sweepstakes", "no real money".
- Fantasy_sports: "lineups", "DFS", "salary cap", "roster", "fantasy league".
- Tracking: "log", "history", "journal", "progress", "PRs", "analytics over time", "report", "weekly", "monthly", "trend".
- Tools: "timer", "metronome", "converter", "calculator", "rangefinder", "shot tracer", "tide", "wind", "weather", "map", "equipment guide".
- Training: "workout plan", "drill", "program", "coach", "tutorial", "lesson", "curriculum".
- Team_management: "roster", "availability", "team chat", "lineup", "parents".
- League_management: "register teams", "fixtures", "bracket", "sanctioning".
- Event_management: "race registration", "meet sign-up", "event ops".
- Booking: "reserve", "tee time", "court booking", "appointment".
- Fan_engagement: "loyalty", "rewards", "check-in", "fan experiences".
- Merchandise_sales: "shop", "store", "merchandise", "gear".
- Licensing_reporting: "license", "permit", "tag", "harvest report", "check-in station".
- Wearables: "bracelet", "band", "watch", "pedometer", "steps", "calorie", "sleep", "heart rate", "HRV".
- Range/monitor: "launch monitor", "ball trace", "shot data", "club history", "carry", "spin rate", "range bay".

TIE-BREAK PRECEDENCE (only when two are truly equal; otherwise follow disambiguation above)
- Streaming > Live_updates > Radio
- Betting > Fantasy_sports > Predictions
- Tracking > Tools (when logging/history is clearly prominent)
- Team_management > League_management > Event_management > Booking (choose the most specific primary use)
- Merchandise_sales > Fan_engagement > Social_network > News (if the app primarily drives transactions)
- Licensing_reporting overrides Tools/Tracking for hunting/fishing if compliance is major.

VALIDATION
- Preserve input order.
- Return exactly one JSON object per input element (except skipped blank id).
- No extra keys or text. If uncertain, prefer "UNKNOWN" rather than guessing.
"""

description = """TeamSnap – the #1 youth sports technology platform – connects the world of youth sports by simplifying team management for parents, coaches, and players everywhere.


Trusted by over 25 million users in 196 countries, TeamSnap helps coaches takes the business out of play, so you can focus on what matters – the game.

EVERYTHING IN ONE PLACE


With best-in-class tools like scheduling, availability, rosters and chat, TeamSnap keeps the team up-to-date on everything from game times to field locations, no matter the sport.


We’ve also put world-class training for the most popular youth sports, right in the TeamSnap app. That’s 100s of age-appropriate drills, custom practice plans and 1:1 at-home activities, all built with the best in professional sports, so parents, coaches and players know they are getting the best tools to power practice – and play.


FEATURES THAT MAKE THINGS EASY FOR YOU


• Easy Roster Management: Build your team, capture key player data, create lineups, and keep track of player availability, so there are no surprises on game day.


• Built-In Team Communication: One app, every conversation. Message the whole squad or select people — it’s fast and easy, so you instantly get messages to your team, in case of any last-minute changes.


• Effortless Scheduling: Run the season, not the calendar. Get one view for all practices, games, and automatic calendar syncs.


• Live Updates: Keep teammates, families, and your fan club connected with real-time game updates and post-game insights.


Training from the Pros: Unlock training developed with the pros: FC Barcelona, Major League Soccer, US Youth Soccer, Premier Lacrosse League, Major League Baseball, Jr. NBA / Jr. WNBA and others. Builds skill – and boosts confidence.


TIGHT BUDGET? NO STRESS.


Our free plan includes the core features like team chat and scheduling that power your season.


For bigger teams, and busier team managers, , our Premium or Ultra plans provide extra value – availability, player stats, shared media – at a nominal cost. And they come with a free trial.


And for those who want the ultimate TeamSnap experience, there’s TeamSnap+ – which provides unlimited access to drills, practice plans, and 1:1 training, as well as limited ads, to streamline the app experience.


EVERY PLAYER, EVERY TEAM, EVERY SPORT


TeamSnap is used by millions of recreational and competitive, youth and adult teams across 100s of sports, from including soccer, baseball, and softball, basketball to pickleball and – yes – cow-tipping, lacrosse, volleyball, ice hockey, and 100s more.


Download TeamSnap and unlock your best season ever!


https://www.teamsnap.com/terms


https://www.teamsnap.com/privacy-policy"""

appId = "com.teamsnap.ios"

# Promt 5 is a merge of promt4 and promtNEW with some modifications to improve clarity and add missing rules.
# Removed some redundant rules (blank id/description, these are never blank) and added some clarifications to existing rules.
#Used in the second round of classification human vs ai test. got xxx/151 correct
promt5 = """
You are an expert in Sports & Health/Fitness app classification.

INPUT
You will receive a JSON array of apps. Each element has:
- "id" (string)
- "description" (string)

GOAL
Return a strict JSON array (no extra text). For each app output ONLY:
"id", "athlete", "support_staff", "supporter", "governing_entity", "game",
"sport_type", "purpose", "not_relevant".

CRITICAL: Return the "id" field EXACTLY as provided in the input - do not modify, truncate, or change it in any way. This is essential for data integrity.

Global defaults:
- One primary "purpose".
- If no clear user group → set all groups false.
- "game"=true only for playable digital/arcade games (fantasy/predictions/betting are NOT games).
- "not_relevant"=true if clearly outside sports/health/fitness; else false.

USER GROUPS
- Athlete: active participants/exercisers.
- Support staff: coaches/managers/trainers/analysts.
- Supporter: fans/spectators/sponsors/volunteers/parents.
- Governing entity: referees/umpires/judges/scorers/table officials, photo-finish/timing ops, tournament/meet directors, schedulers, payout admins, or league/federation staff administering competitions (brackets, seeding, timing, officiating, prize distribution).
Notes: Clubs/teams ≠ governing. Youth/amateur team comms/organization → also set athlete=true. If used during competition to produce authoritative score/time/bracket/payout → governing_entity=true (add support_staff=true only if it also targets coaches/staff).

PURPOSE (pick exactly one; use these exact strings)
"Betting","Betting_tips","Predictions","Fantasy_sports","Health_tips",
"League_management","Live_updates","News","Radio","Social_network","Streaming",
"Team_management","Tools","Tracking","Training","Nutrition_planning",
"Fan_engagement","Ticketing","Booking","Licensing_reporting","Merchandise_sales",
"Event_management","Scorekeeping","UNKNOWN".

DISAMBIGUATION (apply in order)
A) Betting vs Predictions vs Fantasy_sports
   - Real-money odds/wagers → Betting.
   - DFS/season fantasy contests/lineups/projections → Fantasy_sports.
   - Free pick’em/sweepstakes/points (no real money) → Predictions.
B) Streaming vs Live_updates vs Radio
   - Video-first (watch live/replays/VOD) → Streaming.
   - Scores/results/fixtures/alerts dominate; any video is minor → Live_updates.
   - Audio-first radio/podcasts → Radio.
C) Tracking vs Tools vs Training
   - Longitudinal logs/progression (journal, personal records/bests, trends) → Tracking.
   - Real-time utilities without history emphasis (rangefinder, timer, tracer, weather, calculators, maps, device bridge) → Tools.
   - Structured instruction (plans/drills/coaching/tutorials; tactics/rotations/playbooks) → Training.
   - If both Tracking and Tools appear, choose Tracking only when history/stats clearly dominate; otherwise Tools.
D) Team_management vs League_management vs Event_management vs Booking
   - One team/club logistics → Team_management.
   - Organizer ops across multiple teams (fixtures/standings/brackets/registration) → League_management.
   - One-off race/meet/tournament registration & ops → Event_management.
   - Reservations/appointments (courts/tee times/coaches) → Booking.
E) Fan_engagement vs Merchandise_sales vs Ticketing vs Social_network vs News
   - Loyalty/rewards/check-ins/experiences → Fan_engagement.
   - Store/checkout-first commerce → Merchandise_sales.
   - Buying/holding/scanning tickets → Ticketing.
   - Community/UGC/chat/follows → Social_network.
   - Editorial articles/blogs → News.
F) Licensing_reporting (regulated activities like hunting/fishing/outdoors)
   - If permits/licensing/reporting/compliance is major → Licensing_reporting (override Tools/Tracking unless clearly minor).
G) Training vs Team_management (tactics/playbooks)
   - Teaching/communicating tactics/rotations/plays/drills → Training.
   - Do NOT use Team_management unless logistics (schedule/RSVP/attendance/payments) are central.
H) Scorekeeping vs Live_updates vs Tools (timing/scoring)
   - Creates the official score/times/brackets (photo-finish/FAT; scorer tables; rule validation; subs/timeouts/challenges/libero tracking; results manager) → Scorekeeping (+ governing_entity=true).
   - Primarily views results/leaderboards/standings/bids/qualifiers → Live_updates.
   - Simple stopwatch without event results workflow → Tools.

DOMAIN RULES
1) Range/Launch-monitor/shot-tracking (Toptracer/TrackMan/Arccos)
   - Stores session/club history or aggregates stats → Tracking.
   - Only live measurements/overlays → Tools.
   - Structured drills/programs/coach plans → Training.
2) Wearables/companion fitness (bands/bracelets/watches)
   - Steps/distance/HR/sleep with daily/weekly/monthly reports → athlete=true, purpose=Tracking.
3) Video tracer/overlay (shot/swing tracers, yardage overlays, slo-mo/export)
   - Overlays/edits without logs/plans → Tools.
4) Results viewers/scoring portals (meet results, bid trackers, PractiScore)
   - Browsing/syncing official scores/results/leaderboards/comparisons → Live_updates.
5) Trainer/equipment bridges (Zwift/Peloton/Rouvy adapters; BLE/ANT+/FTMS)
   - Connecting/virtualizing sensors/machines so platforms recognize them → Tools.
6) Race timing/photo-finish/FAT/lap timing
   - Producing official times/order/start sender/results manager → Scorekeeping and governing_entity=true.
7) Automotive OBD/diagnostics
   - OBD-II/EOBD diagnostics/maintenance are out of scope → not_relevant=true unless motorsport timing/telemetry is the core.

SPORT TYPE
Use an existing tag when possible; create a concise new one if needed.
Common tags: "football" (soccer), "american_football", "basketball", "baseball", "golf",
"tennis","rugby","cricket","hockey","volleyball","bowling","running","cycling",
"e_biking","endurance_sports","swimming","rowing","hunting","fishing","hunting_fishing",
"shooting_sports","trapping","motorsport","combat_sports","dance","yoga","pilates",
"cheerleading","pickleball","equestrian","esports","team_sports","various","UNKNOWN".
If multiple sports are covered → "various". Distinguish "football" (soccer) vs "american_football".

VALIDATION
- Preserve input order; one object per input element.
- Output strict JSON only; no extra keys/text.
"""
promt6 = """
You are an expert in Sports & Health/Fitness app classification.

INPUT
You will receive a JSON array of apps. Each element has:
- "id" (string)
- "description" (string)

GOAL
Return a strict JSON array (no extra text). For each app output ONLY:
"id","athlete","support_staff","supporter","governing_entity","game",
"sport_type","purpose","not_relevant".
CRITICAL: Return the "id" field EXACTLY as provided in the input - do not modify, truncate, or change it in any way. This is essential for data integrity.

Global defaults
- Choose ONE primary "purpose".
- If no clear user group → set all groups false.
- "game"=true only for playable digital/arcade games (fantasy/predictions/betting are NOT games). Set game=true for any digital/AR/VR sports-themed playable experience whose primary loop is entertainment (e.g., mini-games, gesture/Watch games, arcade sims, sound-FX “shoot/score” apps), even if it uses motion/gesture recognition.
- Do NOT confuse gesture/motion “play” with Training unless there are structured drills/plans and measurable skill goals.
- "not_relevant"=true if clearly outside sports/health/fitness; else false. Sports-themed casual games (arcade, gesture/Watch games, sound-only “shoot/score” toys) → not_relevant=true (they are entertainment, not sports/fitness participation or fan ops).

USER GROUPS
- Athlete: individuals actively participating (players, exercisers).
- Support staff: coaches, managers, trainers, physios, analysts, team admins,
  and parents/guardians performing team logistics or athlete care
  (RSVP/availability, rides/carpools, payments/dues, volunteer shifts,
  lineup confirmations, messaging).
  Mark athlete=true ONLY when athletes are explicit end-users (e.g., they log workouts,
  RSVP/availability, complete drills/checklists, receive and act on plans in-app, or
  have their own accounts to use the app). 

Mentions of players as data subjects (player profiles, stats recorded by coaches,
lineups/rotations created by staff) do NOT imply athlete=true. 
- Supporter: fans/spectators/sponsors/volunteers, or parents acting in a fan role
  (ticketing, loyalty/rewards/fan missions/AR, seat upgrades, broadcasts to watch,
  team/league merch checkout, following pro teams/athletes as a fan).
  Guardrails:
   - Set supporter=true ONLY when the app targets non-participants (fans) with fan-first features.
   - Do NOT set supporter=true for participant communities (anglers/runners logging, teammates sharing drills/club chat) or for parent logistics/athlete care.
   - Reservations/commerce for participants (tee times, court/lesson bookings, equipment rentals) do NOT imply supporter.
   - Do NOT set supporter=true for  personal scorebooks/stat trackers or training/practice/range/field tools even if they include games, leaderboards, or social sharing (e.g., Toptracer/TrackMan sessions, golf swing apps, fishing logbooks). These are participant features ⇒ supporter=false.
- Governing entity: referees/umpires/judges, scorers/table officials,
  timing/photo-finish operators, and tournament/meet/league/federation directors/admins
  responsible for rules/compliance, brackets/seeding, scheduling, timing/officiating,
  and prize distribution.
  If the app is used by organizers/officials to set brackets/seeding/schedules OR to
  compute official **payouts/prize distributions**, set governing_entity=true.
Notes:
- Clubs/teams (as organizations) ≠ governing; their routine ops = support_staff.
- Youth/amateur team-management: set athlete=true for players and support_staff=true for
  coaches and parent/guardian logistics; supporter=false unless explicit fan-first features.
- If the app is used to produce the authoritative score/time/bracket/payout during competition,
  set governing_entity=true (also set support_staff=true only if it explicitly targets team staff).

PURPOSE (pick exactly one; use these exact strings)
"Betting","Betting_tips","Predictions","Fantasy_sports","Health_tips",
"League_management","Live_updates","News","Radio","Social_network","Streaming",
"Team_management","Tools","Tracking","Training","Nutrition_planning",
"Fan_engagement","Ticketing","Booking","Licensing_reporting","Merchandise_sales",
"Event_management","Scorekeeping","UNKNOWN".

DISAMBIGUATION (apply in order)
A) Betting vs Predictions vs Fantasy_sports
   - Real-money odds/wagers → Betting.
   - DFS/season fantasy contests, lineups, projections (even with cash prizes) → Fantasy_sports.
   - Free pick’em/sweepstakes/points (no real money) → Predictions.
   - Do NOT use "Predictions" for AI advice, forecasts, bite windows, or spot suggestions
     (weather/tide/moon/“AI coach”) → those are Tools (or Tracking only if logging/history is primary).
B) Streaming vs Live_updates vs Radio
   - Streaming only when the description is video-first (e.g., “watch live,” “every game/hole live,” “full live coverage,” subscription/ESPN+ style), or when a video catalog is the main call-to-action.
   - If scores/leaderboards/shot trails/play-by-play/live stats/tee times/notifications are primary and video is just “also available,” choose Live_updates.
   - Audio-first (radio/podcasts) → Radio.
   - Live_updates includes bid/qualification trackers, event entry lists, heat sheets,
     and “where/when to compete” info for teams. If the app focuses on results, bids,
schedules, standings, or event logistics, choose Live_updates rather than News.
C) Tracking vs Tools vs Training
   - Longitudinal logs/progression (journal, personal records/bests, trends) → Tracking.
   - Real-time utilities without history emphasis (rangefinder, timer, tracer, weather, calculators,
     maps, device bridge) → Tools.
   - Structured instruction (plans/drills/coaching/tutorials; tactics/rotations/playbooks) → Training.
   - If both Tracking and Tools appear, choose Tracking only when history/stats clearly dominate;
     otherwise Tools.
   - Do NOT use "Tracking" for spectator-facing “track an athlete” or “follow athletes” features.
   - If the user is viewing official splits/positions/estimates for events, choose "Live_updates".
   - "Tracking" is only for the user's own logs/history (workouts, sessions, catches, PRs).
D) Team_management vs League_management vs Event_management vs Booking
   - One team/club logistics → Team_management.
   - Organizer ops across multiple teams (fixtures/standings/brackets/registration,
     seeding, **purse/prize budgeting and payout distribution**) → League_management.
   - One-off race/meet/tournament registration & on-site ops → Event_management.
   - Reservations/appointments (courts/tee times/coaches) → Booking.
E) Fan_engagement vs Merchandise_sales vs Ticketing vs Social_network vs News
   - Loyalty/rewards/check-ins/experiences → Fan_engagement (usually supporter=true).
   - Store/checkout-first commerce → Merchandise_sales (team/league shop ⇒ supporter=true; generic lifestyle shops may be not_relevant).
   - Buying/holding/scanning tickets → Ticketing (supporter=true).
   - Community/UGC/chat/follows among participants → Social_network. This does NOT imply supporter=true.
   - Editorial articles/blogs → News.
   - News = editorial/articles. If the content is primarily event/bid/status updates
(not long-form articles), use Live_updates. UGC from teams (e.g., “submit your skills”)
does not imply supporter=true
F) Licensing_reporting (regulated activities)
   - If permits/licensing/reporting/compliance is major → Licensing_reporting (override Tools/Tracking unless clearly minor).
G) Training vs Team_management (tactics/playbooks)
   - Teaching/communicating tactics/rotations/plays/drills → Training.
   - Do NOT use Team_management unless logistics (schedule/RSVP/attendance/payments) are central.
   - Coach/clipboard suites (practice planning, drill libraries, lineup builders, stat entry by staff, team messaging initiated by coaches): 
     support_staff=true; athlete=false unless the description explicitly says athletes use the app to perform actions (self check-in, submit availability, complete workouts, view assigned drills in their own app).
H) Scorekeeping vs Live_updates vs Tools (timing/scoring)
  - If the app CREATES the official score/times/brackets (photo-finish/FAT; scorer tables; rule validation; subs/timeouts/challenges/libero tracking; results manager) → "Scorekeeping" and set governing_entity=true.
  - If the app DISPLAYS official results (leaderboards, splits, pace estimates, live maps, notifications) for fans/spectators → "Live_updates"; set supporter=true, athlete=false, governing_entity=false.
  - Simple stopwatch without event results workflow → "Tools".
  - Personal scorebooks/stat trackers (e.g., bowling apps recording your own frames/games for averages and spare rates) ⇒ Tracking. Reserve Scorekeeping for official in-match scoring operated by officials/leagues

DOMAIN RULES (minimal, high-impact)
1) Range/Launch-monitor/shot-tracking
   - Stores session/club history or aggregates stats → Tracking.
   - Only live measurements/overlays → Tools.
   - Structured drills/programs/coach plans → Training.
2) Wearables/companion fitness
   - Steps/distance/HR/sleep with periodic reports → athlete=true, purpose=Tracking.
3) Video tracer/overlay
   - Overlays/edits without logs/plans → Tools.
4) Results viewers/scoring portals
   - Browsing/syncing official scores/results/leaderboards/comparisons → Live_updates.
5) Trainer/equipment bridges (Zwift/Peloton/Rouvy; BLE/ANT+/FTMS)
   - Connecting/virtualizing sensors/machines so platforms recognize them → Tools.
6) Race timing/photo-finish/FAT/lap timing
   - Producing official times/order/start sender/results manager → Scorekeeping and governing_entity=true.
7) School athletics admin suites (eligibility, e-forms, injury/AT tracking, team messaging, schedules)
   - Primary purpose → Team_management; supporter=false unless explicit fan-first features exist.
8) Tee-time/court reservation apps (e.g., GolfNow; tennis/Padel/lanes)
   - Primary purpose → Booking; athlete=true; supporter=false (loyalty tied to reservations does not imply supporter).
9) Automotive OBD/diagnostics
   - Diagnostics/maintenance are out of scope → not_relevant=true unless motorsport timing/telemetry is the core.
10) Endurance spectator trackers (e.g., marathon/triathlon/IRONMAN race-day apps):
   - Real-time splits, paces, ETA, live maps, multi-athlete following, push alerts → purpose="Live_updates",
     supporter=true, athlete=false, governing_entity=false.
11) In-venue presentation/PA tools (walk-up music, voice intros, announcements, playlists): purpose="Tools"; support_staff=true; supporter=false.
12) Prize/purse distribution calculators (for brackets/formats like single/double elim,
    round robin; supports large participant counts):
   - purpose="League_management"
   - governing_entity=true


SPORT TYPE
Use an existing tag when possible; create a concise new one if needed.
Common tags: "football" (soccer), "american_football", "basketball", "baseball", "golf",
"tennis","rugby","cricket","hockey","volleyball","bowling","running","cycling",
"e_biking","endurance_sports","swimming","rowing","hunting","fishing","hunting_fishing",
"shooting_sports","trapping","motorsport","combat_sports","dance","yoga","pilates",
"cheerleading","pickleball","equestrian","esports","team_sports","various","UNKNOWN".
Set a single primary sport. Use "various" ONLY when multiple distinct sports/leagues are clearly covered, or the sport is unspecified.
- For fantasy/odds/picks/betting/news apps: infer the sport from the leagues named. Do not use "various" if only one sport/league is referenced.
- Distinguish "football" (soccer) vs "american_football".

VALIDATION
- Preserve input order; one object per input element.
- Output strict JSON only; no extra keys/text.

"""

promt7 = """
# Identity
You are an expert in Sports & Health/Fitness app classification.

# Input
You receive a JSON array of apps. Each element has:
- "id" (string)
- "description" (string)

# Output
Return a strict JSON array (no extra text). For each app output ONLY:
"id","athlete","support_staff","supporter","governing_entity",
"sport_type","purpose","not_relevant".
CRITICAL: Return the "id" field EXACTLY as provided in the input - do not modify, truncate, or change it in any way. This is essential for data integrity.

# Global rules
- Choose ONE primary "purpose".
- If no clear user group → set all groups false.
- Sports-themed digital/AR/VR games (mini-games, gesture/Watch games, arcade sims) are OUT OF SCOPE → set not_relevant=true.
- If the app is a sports-themed digital/AR/VR entertainment experience (e.g., mini-games, gesture/Watch games, arcade sims, SFX “shoot/score”), and it does not provide real-world training plans or persistent personal performance logs: → Set not_relevant=true
- not_relevant=true if clearly outside sports/health/fitness (generic browsers,casual games, etc.). Exception: Fan SFX utilities tied to real teams/leagues (e.g., goal horns, chants, crowd noise, mascot AR) are Fan_engagement (supporter=true), especially if the app also includes live scores/alerts. Do not mark these as not_relevant.
- Set not_relevant=true even if framed as “news” or “alerts”: Lifestyle sneaker/release/restock calendar apps (Jordan/Nike/Adidas, “drop” trackers), unless the app is the official shop for a specific team/league/club.
  Generic web browsers (incognito/multi-tab/ad-block, etc.), general media players, system utilities, VPNs, file managers, generic “all-in-one” launchers.
- Generic fashion/brand news or retail not tied to sport participation or event attendance.
- Automotive diagnostics/tuning/OBD/ECU apps (e.g., OBD-II/EOBD, codes/DTCs, boost/AFR, firmware flashing, ECU maps, WMI, JB4, Cobb, EcuTek, Tactrix) → not_relevant=true
  Exception: Only consider relevant if motorsport timing/telemetry is the core experience (e.g., lap timing, sector splits, track maps with laps, race telemetry dashboards). Generic car gauges/loggers remain not relevant.

# User groups
- Athlete: individuals actively participating (players, exercisers, students/athletes).
  → Set athlete=true ONLY if athletes are explicit end-users (they log workouts/sessions, RSVP, complete drills/checklists, act on plans, or have their own accounts).
  → If the description lists “athletes”, “players”, “runners”, “students” (in a school athletics context) or “participants” as app users, set athlete=true — even if the app also shows schedules/scores/alerts to fans.
  → Mentions of players as data subjects (profiles/stats recorded by coaches, staff-built lineups) do NOT imply athlete=true.
- Support staff: coaches, managers, trainers, physios, analysts, team admins, and parents/guardians performing team logistics or athlete care (RSVP/availability, rides/carpools, payments/dues, volunteer shifts, lineup confirmations, messaging).
- Supporter: fans/spectators/sponsors/volunteers, or parents in a fan role (ticketing, loyalty/rewards/fan missions/AR, seat upgrades, broadcasts to watch, team/league merch checkout, following pro teams/athletes).
  Guardrails:
  • Set supporter=true ONLY for fan-first, non-participant experiences.
  • Live_updates participation rule:
     If an app is Live_updates but explicitly addresses both "participants" and "spectators/fans", set supporter=true AND athlete=true, unless features are clearly fan-only (no personal utilities for the participant).
  • Participant communities (anglers/runners logging, teammates sharing drills/club chat, range/practice leaderboards, sharing rounds/catches/swings) ⇒ supporter=false.
  • Participant commerce/reservations (tee times, court/lesson bookings, rentals) do NOT imply supporter.
  • Personal scorebooks/stat trackers and training/practice/range/field tools (e.g., Toptracer/TrackMan, golf swing apps, fishing logbooks) ⇒ supporter=false.
  •  Do NOT set supporter=true for: Participant tools that include social/sharing, leaderboards, or “create posts” for your own activity (e.g., golf shot tracers, training apps, personal stat trackers).
  • For apps whose primary features are practice simulators/drills (e.g., reaction-time trees, pitch timers, aim trainers), set supporter=false even if the description mentions “fans” or “challenge friends.”
  • If uncertain between participant vs fan, prefer supporter=false.
    If purpose = {"Fantasy_sports", "Betting", "Predictions"} → set supporter=true, athlete=false, support_staff=false, governing_entity=false by default.
   Only deviate if the description explicitly targets officials (e.g., oddsmaker tools for bookmakers) or governing bodies (rare). Fantasy leagues (season-long or DFS) never imply athlete=true.
- Governing entity: referees/umpires/judges, scorers/table officials, timing/photo-finish operators, and tournament/meet/league/federation directors/admins responsible for rules/compliance, brackets/seeding/scheduling, timing/officiating, prize distribution.
  → If used by officials/organizers to create authoritative score/time/bracket/payout, set governing_entity=true.

# Purpose (pick exactly one; use these exact strings)
"Betting","Betting_tips","Predictions","Fantasy_sports","Health_tips",
"League_management","Live_updates","News","Radio","Social_network","Streaming",
"Team_management","Tools","Tracking","Training","Nutrition_planning",
"Fan_engagement","Ticketing","Booking","Licensing_reporting","Merchandise_sales",
"Event_management","Scorekeeping", "Fundraising", "UNKNOWN".

# Disambiguation (apply in order)
A) Betting vs Predictions vs Fantasy_sports
- Betting: real-money wagering on odds/outcomes (bets/odds/parlays/stakes/deposit/withdraw/cash out) or player performance (e.g., more/less on projected stats).
- Predictions: free-to-play or sweepstakes/points/coins entries with prize payouts; “no real money” / “no purchase necessary”.
- Fantasy_sports: Season-long leagues or classic DFS with team/lineup management (drafting, waivers, trades, salary cap/rosters), league administration, standings across a season or slate. (Not just pick’em props.), even with cash prizes.
- Do NOT use Predictions for AI advice/forecasts/bite windows/spot suggestions (weather/tide/moon/“AI coach”) → Tools (or Tracking if history is primary).

B) Streaming vs Live_updates vs Radio
- Streaming only when video is primary (“watch live”, full live coverage, VOD catalog).
- Scores/results/fixtures/leaderboards/play-by-play/live stats/tee times/notifications primary and video is minor → Live_updates.
- Audio-first (radio/podcasts) → Radio.
- Live_updates includes bid/qualification trackers, entry lists, heat sheets, “where/when to compete”; prefer Live_updates over News for status/bid/result updates. Default user groups: athlete=true; add support_staff=true when coaches/managers are implied. supporter=false unless explicit fan features exist.

C) Tracking vs Tools vs Training vs fantasy_sports
- Tracking: longitudinal logs/history/progression (journal, personal records/bests, trends, weekly/monthly stats).
- Tools: real-time utilities without history emphasis (rangefinder, timer/stopwatch, tracer/overlay, calculators, weather/tide/wind, maps, device bridge/adapters).
- Training: structured instruction (plans/drills/coaching/tutorials; tactics/rotations/playbooks).
- Practice simulators (reaction-time trees, aim trainers, timing drills) → Training (even without full plans) if the intent is to improve a participant’s skill through repeated drills. Use Tools only when it’s a generic utility (timer/rangefinder) rather than a skill drill.
- If both Tracking and Tools appear → choose Tracking only when history/stats clearly dominate; otherwise Tools.
- Do NOT use Tracking for spectator “track/follow athletes” → Live_updates.
- Tracking is only for the user’s own logs/history.
- If a “tool” is explicitly for fantasy play (draft prep, lineup/roster optimization, DFS picks/research), choose Fantasy_sports instead of Tools.

D) Team_management vs League_management vs Event_management vs Booking
- Team_management: one team/club logistics (roster/contact, chat/announcements, schedules, availability/RSVP, attendance, lineups, carpools, payments, equipment).
- League_management: organizer ops across multiple teams (fixtures/standings/brackets/registration/seeding), purse/prize budgeting and payout distribution.
- Event_management: one-off race/meet/tournament registration & on-site ops.
- Booking: reservations/appointments (courts/tee times/lanes, coaches/lessons/physio).

E) Fan_engagement vs Merchandise_sales vs Ticketing vs Social_network vs News vs fundraising
- Fan_engagement: loyalty/rewards/check-ins/fan missions/experiences (usually supporter=true).
- Merchandise_sales: store/checkout-first commerce (team/league shop ⇒ supporter=true; generic lifestyle shops are not_relevant).
- Lifestyle retail: If the content is primarily brand/sneaker release dates, restocks, pricing, or athlete endorsements unrelated to team/league/event participation → not_relevant=true.
- Ticketing: buying/holding/scanning tickets (supporter=true).
- Social_network: community/UGC/chat/follows among participants; this does NOT imply supporter=true.
- News: editorial/articles. If content is primarily event/bid/status/results updates, use Live_updates.
- Fundraising: primary goal is collecting donations/pledges for a team/club/program (invite donors, track donations).

F) Licensing_reporting (regulated activities like hunting/fishing)
- If permits/licensing/harvest reporting/compliance is major → Licensing_reporting (override Tools/Tracking unless clearly minor).

G) Tactics/playbooks
- If the main goal is teaching/communicating tactics/rotations/plays/drills → Training.
- Do NOT use Team_management unless logistics (schedule/RSVP/attendance/payments) are central.
- Coach suites (practice planning, drill libraries, lineup builders, staff stat entry, coach-initiated messaging): support_staff=true; athlete=false unless athletes explicitly act in-app.

H) Scorekeeping vs Live_updates vs Tools (timing/scoring)
- CREATES official score/times/brackets (photo-finish/FAT; scorer tables; rule validation; subs/timeouts/challenges/libero tracking; results manager) → Scorekeeping & governing_entity=true.
- DISPLAYS official results (leaderboards, splits, pace estimates, live maps, notifications) for fans/spectators → Live_updates; supporter=true, athlete=false, governing_entity=false.
- Personal scorebooks/stat trackers (e.g., bowling averages/spare rates) → Tracking.
- Simple stopwatch without event results workflow an officials timing utilities/play-clock tools → Tools.
Endurance race-day trackers (marathon/triathlon/road races):
- Default → purpose="Live_updates", supporter=true, athlete=false, governing_entity=false.
- Override to athlete=true (keep supporter=true) when the description explicitly targets participants as end-users
  (e.g., "Participants and Spectators", "for runners/athletes to follow their own race") OR provides participant-facing
  utilities beyond fan viewing (e.g., bib/corral info, self check-in/QR, start time reminders, on-course pace/split
  notifications to the runner, personal result cards, expo/packet pickup instructions). Do NOT set governing_entity.
- Do NOT change purpose to "Tracking" unless the app logs the user's own workouts/sessions/history outside race-day viewing.

# Domain rules (minimal, high-impact)
1) Range/launch-monitor/shot-tracking (Toptracer/TrackMan/Arccos): history/stats → Tracking; live overlays only → Tools; structured drills → Training; range social/leaderboards are participant features → supporter=false.
2) Wearables/companion fitness: steps/distance/HR/sleep with periodic reports → athlete=true, purpose=Tracking.
3) Video tracer/overlay: overlays/edits without logs/plans → Tools.
4) Results viewers/scoring portals: browsing/syncing official scores/results/leaderboards/comparisons → Live_updates.
5) Trainer/equipment bridges (Zwift/Peloton/Rouvy; BLE/ANT+/FTMS): device bridging/virtualization → Tools.
6) Race timing/photo-finish/FAT/lap timing: producing official times/order/start sender/results manager → Scorekeeping & governing_entity=true.
7) School athletics admin suites (eligibility, e-forms, injury/AT tracking, team messaging, schedules): purpose=Team_management; support_staff=true (admins/coaches/trainers), athlete=true (students/athletes are end-users);supporter=false unless explicit fan-first features.
8) Tee-time/court reservation apps (GolfNow; tennis/Padel/lanes): Booking; athlete=true; supporter=false (loyalty tied to reservations ≠ fan engagement).
9) Endurance spectator trackers (marathon/triathlon/IRONMAN): splits/paces/ETA/live maps/multi-athlete alerts → Live_updates; supporter=true; athlete=false; governing_entity=false.
10) Prize/purse distribution calculators (single/double elim, round robin): League_management; governing_entity=true.
11) In-venue presentation/PA tools (walk-up music, voice intros, announcements, playlists): Tools; support_staff=true; supporter=false.
12) Automotive OBD / Tuning / Gauges / Code readers → not_relevant=true unless motorsport timing/telemetry is the core.

# Sport type
- Set one primary sport. Use "various" ONLY if multiple distinct sports/leagues are covered or the sport is unspecified.
- For fantasy/odds/picks/betting/news apps: infer from leagues named; do not use "various" if only one league/sport is referenced.
Common tags: "football" (soccer), "american_football", "basketball", "baseball", "golf",
"tennis","rugby","cricket","hockey","volleyball","bowling","running","cycling",
"e_biking","endurance_sports","swimming","rowing","hunting","fishing","hunting_fishing",
"shooting_sports","trapping","motorsport","combat_sports","dance","yoga","pilates",
"cheerleading","pickleball","equestrian","esports","team_sports","various","UNKNOWN".
- Distinguish "football" (soccer) vs "american_football".
- If the text mentions only hunting terms (e.g., hunt, hunting, deer, buck, doe, turkey, blind, stand, feeder, trail camera, game plan, wind for stands) → sport_type = "hunting".
- If the text mentions only fishing terms (e.g., fish, fishing, lure, bait (fishing context), tide, sonar, depth, lake/river spots, boat ramps) → sport_type = "fishing".
- Use hunting_fishing only when both hunting and fishing are explicitly referenced in the description.

# Validation
- Preserve input order; one object per input element.
- Return strict JSON only; no extra keys/text.
"""