// Central storage for prompt templates used in the classifier (JS module)
export const promt1 = `
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

Description: `;

export const promt2 = `Developer: You are an expert in sports and health & fitness HCI research and application classification.

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
]`;

export const description = `TeamSnap – the #1 youth sports technology platform – connects the world of youth sports by simplifying team management for parents, coaches, and players everywhere.


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


https://www.teamsnap.com/privacy-policy`;

export const appId = "com.teamsnap.ios";
