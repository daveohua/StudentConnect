# StudentConnect

StudentConnect is a web app that allows students to:
- Create an account and log in using a magic link sent to their email address
- Upload, edit and save their lesson timetable
- Compare their timetable with other students, highlighting free periods in common
- Control who sees their timetable

It uses Flask as a web framework, Jinja to generate webpages and emails and JWT to generate authentication tokens.

This was my first full Python project. I learned how to use objects and modules to my advantage, and I was able to learn how to use the Flask framework on top of integrating different packages to achieve my goals. In the future I plan onccleaning up the code and adding full documentation, then I will plan and write formal tests. The database and objects are modelled on the idiosyncrasies of my former college, so I will likely iron those out to bring attention to the more important techniques I have developed writing this programme.

## How to run (testing only)

1. Set up a virtual environment with flask and PyJWT installed.
2. Run flask --app studentconnect init-db in the root of the project, to initialise the database.
3. Run flask --app studentconnect run in the root of the project, to run the app locally.

