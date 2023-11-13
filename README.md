# Capstone
## Website Name: Optimal
#### Visit the site here: https://optimal-capstone-app.onrender.com/

### About
The goal of my website is to help patients taking antidepressants find the best drug for them. It will incorporate some of the features of a "mood tracker"
app, but will also have some unique features. It can be difficult to rate the effectiveness of an antidepressant, because there are so many outside factors
that can affect our mood. By having the user record how they feel each day, we can use this
data to quantify the effectiveness of the drug(s) they are taking. That way, a patient can see to what degree the drug is working, and will have better,
more quantitative feedback to give their doctor than “I think it’s helping”, or, “It’s not helping”.

### API Update  
The API that I am using is a motivational quote API called Quotel. I decided to use this API for the time being because the medicine API can only retrieve very large blocks of text that are too verbose for my application. I'm planning on instead building my own database with the top 100 or so medications and then linking this to my application.  

The API that I will eventually be using is called DrugAPI.  https://rapidapi.com/ddowar-1g0Q3PyrJyP/api/drugapi
It isn't maintained by a company, but rather an individual. Most of the Drug-Related APIs I found were either 1) Not free (i.e. myHealthBox), or 2) The information they had was too verbose for my application, and it would've been a pain to try to parse out the relevant information.
### Features Implemented
1. User signup and login.
2. A daily mood survey that the user can take after logging in.
3. Email reminders: If the survey is not completed by a certain time each day, the user is sent a reminder.
4. Personal summary: A personal summary is generated every week for each user. This includes average scores and a "medication effectiveness score" (more on this later). A user can also look back at past weeks to compare.
5. Ability to edit one's user info or delete their account. 
6. Daily Quote: A famous quote is displayed on the homepage after logging in. This is fetched from an API and changes daily. I think this is good to have because taking the same survey every day can get boring. So having something that changes from day to day helps keep things fresh.

### User Flow
Start at homepage -> Click "Sign Up" -> Enter basic info -> Enter External Factors -> Enter Medications you are taking (optional) -> Finish signup -> Now inside the member area -> Take daily survey

### Tech Stack
- Flask (Backend server)
- SQLAlchemy as ORM
- Jinja for HTML templates
- PostgreSQL for database
- WTForms for signup and daily survey forms
- bCrypt for authentication
- APScheduler to schedule background tasks
- Bootstrap for styling
- jQuery for client-side JS
