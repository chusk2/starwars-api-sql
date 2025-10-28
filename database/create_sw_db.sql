-- Create the database if it doesn't exist and then select it for use.
CREATE DATABASE IF NOT EXISTS starwars ;
USE starwars ;

--
-- Main Entity Tables
--

-- Table for Planets
CREATE TABLE IF NOT EXISTS planets (
    planet_id INT PRIMARY KEY,
    name VARCHAR(255),
    rotation_period INT,
    orbital_period INT,
    diameter INT,
    climate VARCHAR(255),
    gravity VARCHAR(255),
    terrain VARCHAR(255),
    surface_water INT,
    population_millions INT,
    url VARCHAR(255)
);

-- Table for Species
CREATE TABLE IF NOT EXISTS species (
    species_id INT PRIMARY KEY,
    name VARCHAR(255),
    classification VARCHAR(255),
    designation VARCHAR(255),
    average_height INT,
    skin_colors VARCHAR(255),
    hair_colors VARCHAR(255),
    eye_colors VARCHAR(255),
    average_lifespan INT,
    homeworld_id INT,
    language VARCHAR(255),
    url VARCHAR(255),
    FOREIGN KEY (homeworld_id) REFERENCES planets(planet_id)
);

-- Table for Starships
CREATE TABLE IF NOT EXISTS starships (
    starship_id INT PRIMARY KEY,
    name VARCHAR(255),
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    cost_in_credits BIGINT,
    length FLOAT,
    max_atmosphering_speed INT,
    crew INT,
    passengers INT,
    cargo_capacity BIGINT,
    consumables VARCHAR(150),
    hyperdrive_rating INT,
    MGLT INT,
    starship_class VARCHAR(255),
    url VARCHAR(255)
);

-- Table for Vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT PRIMARY KEY,
    name VARCHAR(255),
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    cost_in_credits INT,
    length FLOAT,
    max_atmosphering_speed INT,
    crew INT,
    passengers INT,
    cargo_capacity INT,
    consumables VARCHAR(150),
    vehicle_class VARCHAR(255),
    url VARCHAR(255)
);

-- Table for Films
CREATE TABLE IF NOT EXISTS films (
    film_id INT PRIMARY KEY,
    title VARCHAR(255),
    episode INT,
    opening_crawl TEXT,
    director VARCHAR(255),
    producer VARCHAR(255),
    release_date DATE,
    url VARCHAR(255)
);

-- Table for People (Characters)
CREATE TABLE IF NOT EXISTS people (
    character_id INT PRIMARY KEY,
    name VARCHAR(255),
    height INT,
    mass INT,
    hair_color VARCHAR(50),
    skin_color VARCHAR(50),
    eye_color VARCHAR(50),
    birth_year VARCHAR(20),
    gender VARCHAR(20),
    homeworld_id INT,
    species_id INT,
    url VARCHAR(255),
    FOREIGN KEY (homeworld_id) REFERENCES planets(planet_id),
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);

--
-- Junction Tables for Many-to-Many Relationships
--

-- People (Pilots) <-> Starships
CREATE TABLE IF NOT EXISTS people_starships (
    character_id INT,
    starship_id INT,
    PRIMARY KEY (character_id, starship_id),
    FOREIGN KEY (character_id) REFERENCES people(character_id),
    FOREIGN KEY (starship_id) REFERENCES starships(starship_id)
);

-- People (Pilots) <-> Vehicles
CREATE TABLE IF NOT EXISTS people_vehicles (
    character_id INT,
    vehicle_id INT,
    PRIMARY KEY (character_id, vehicle_id),
    FOREIGN KEY (character_id) REFERENCES people(character_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

-- Films <-> People (Characters)
CREATE TABLE IF NOT EXISTS films_people (
    film_id INT,
    character_id INT,
    PRIMARY KEY (film_id, character_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (character_id) REFERENCES people(character_id)
);

-- Films <-> Planets
CREATE TABLE IF NOT EXISTS films_planets (
    film_id INT,
    planet_id INT,
    PRIMARY KEY (film_id, planet_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (planet_id) REFERENCES planets(planet_id)
);

-- Films <-> Starships
CREATE TABLE IF NOT EXISTS films_starships (
    film_id INT,
    starship_id INT,
    PRIMARY KEY (film_id, starship_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (starship_id) REFERENCES starships(starship_id)
);

-- Films <-> Vehicles
CREATE TABLE IF NOT EXISTS films_vehicles (
    film_id INT,
    vehicle_id INT,
    PRIMARY KEY (film_id, vehicle_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

-- Films <-> Species
CREATE TABLE IF NOT EXISTS films_species (
    film_id INT,
    species_id INT,
    PRIMARY KEY (film_id, species_id),
    FOREIGN KEY (film_id) REFERENCES films(film_id),
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);


