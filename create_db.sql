-- Create the database if it doesn't exist and then select it for use.
CREATE DATABASE IF NOT EXISTS starwars_db;
USE starwars_db;

--
-- Main Entity Tables
--

-- Table for Films
CREATE TABLE IF NOT EXISTS films (
    film_id INT PRIMARY KEY,
    title VARCHAR(255),
    episode_id INT,
    opening_crawl TEXT,
    director VARCHAR(255),
    producer VARCHAR(255),
    release_date DATE
);

-- Table for People (Characters)
CREATE TABLE IF NOT EXISTS people (
    people_id INT PRIMARY KEY,
    name VARCHAR(255),
    height VARCHAR(10),
    mass VARCHAR(10),
    hair_color VARCHAR(50),
    skin_color VARCHAR(50),
    eye_color VARCHAR(50),
    birth_year VARCHAR(20),
    gender VARCHAR(20),
    homeworld_id INT,
    species_id INT,
    FOREIGN KEY (homeworld_id) REFERENCES planets(planet_id),
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);

-- Table for Planets
CREATE TABLE IF NOT EXISTS planets (
    planet_id INT PRIMARY KEY,
    name VARCHAR(255),
    rotation_period VARCHAR(40),
    orbital_period VARCHAR(40),
    diameter VARCHAR(40),
    climate VARCHAR(255),
    gravity VARCHAR(255),
    terrain VARCHAR(255),
    surface_water VARCHAR(40),
    population VARCHAR(40)
);

-- Table for Species
CREATE TABLE IF NOT EXISTS species (
    species_id INT PRIMARY KEY,
    name VARCHAR(255),
    classification VARCHAR(255),
    designation VARCHAR(255),
    average_height VARCHAR(40),
    skin_colors VARCHAR(255),
    hair_colors VARCHAR(255),
    eye_colors VARCHAR(255),
    average_lifespan VARCHAR(40),
    homeworld_id INT,
    language VARCHAR(255),
    FOREIGN KEY (homeworld_id) REFERENCES planets(planet_id)
);

-- Table for Starships
CREATE TABLE IF NOT EXISTS starships (
    starship_id INT PRIMARY KEY,
    name VARCHAR(255),
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    cost_in_credits VARCHAR(40),
    length VARCHAR(40),
    max_atmosphering_speed VARCHAR(40),
    crew VARCHAR(40),
    passengers VARCHAR(40),
    cargo_capacity VARCHAR(40),
    consumables VARCHAR(40),
    hyperdrive_rating VARCHAR(40),
    MGLT VARCHAR(40),
    starship_class VARCHAR(255)
);

-- Table for Vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT PRIMARY KEY,
    name VARCHAR(255),
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    cost_in_credits VARCHAR(40),
    length VARCHAR(40),
    max_atmosphering_speed VARCHAR(40),
    crew VARCHAR(40),
    passengers VARCHAR(40),
    cargo_capacity VARCHAR(40),
    consumables VARCHAR(40),
    vehicle_class VARCHAR(255)
);


--
-- Junction Tables for Many-to-Many Relationships
--

-- Films <-> People (Characters)
CREATE TABLE IF NOT EXISTS films_people_junction (
    film_id INT,
    people_id INT,
    PRIMARY KEY (film_id, people_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (people_id) REFERENCES people(people_id)
);

-- Films <-> Planets
CREATE TABLE IF NOT EXISTS films_planets_junction (
    film_id INT,
    planet_id INT,
    PRIMARY KEY (film_id, planet_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (planet_id) REFERENCES planets(planet_id)
);

-- Films <-> Starships
CREATE TABLE IF NOT EXISTS films_starships_junction (
    film_id INT,
    starship_id INT,
    PRIMARY KEY (film_id, starship_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (starship_id) REFERENCES starships(starship_id)
);

-- Films <-> Vehicles
CREATE TABLE IF NOT EXISTS films_vehicles_junction (
    film_id INT,
    vehicle_id INT,
    PRIMARY KEY (film_id, vehicle_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

-- Films <-> Species
CREATE TABLE IF NOT EXISTS films_species_junction (
    film_id INT,
    species_id INT,
    PRIMARY KEY (film_id, species_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);

-- People (Pilots) <-> Starships
CREATE TABLE IF NOT EXISTS people_starships_junction (
    people_id INT,
    starship_id INT,
    PRIMARY KEY (people_id, starship_id),
    FOREIGN KEY (people_id) REFERENCES people(people_id),
    FOREIGN KEY (starship_id) REFERENCES starships(starship_id)
);

-- People (Pilots) <-> Vehicles
CREATE TABLE IF NOT EXISTS people_vehicles_junction (
    people_id INT,
    vehicle_id INT,
    PRIMARY KEY (people_id, vehicle_id),
    FOREIGN KEY (people_id) REFERENCES people(people_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);
