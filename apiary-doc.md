FORMAT: 1A
HOST: http://openbikes.co/api

# OpenBikes

## City geoJSON [/geojson/{city}]

OpenBikes shapes the data collected from various APIs into a common format. This route returns the latest data for a specified city.


+ Parameters
    + city - `Toulouse` (string) The city which you want to access.

### Retrieve latest geoJSON of a city [GET]

+ Response 200 (application/json)

        {
            status: "success",
            features: [
                {
                    geometry: {
                        coordinates: [
                            1.441003598726198,
                            43.608951960496405
                        ],
                        type: "Point"
                    },
                    properties: {
                        address: "2 RUE GATIEN ARNOULT",
                        bikes: 3,
                        lat: 43.608951960496405,
                        lon: 1.441003598726198,
                        name: "00055 - ST SERNIN G. ARNOULT",
                        stands: 12,
                        status: "OPEN",
                        update: "2016-03-10T16:57:48"
                    },
                    type: "Feature"
                }
            ]
        }

## Country names [/countries?name={name}&provider={provider}]

Each country contains multiple stations.

+ Parameters
    + name - `France` (string) The country you want to filter by.
    + provider - `jcdecaux` (string) The provider you want to filter by.

### Retrieve country names [GET]

+ Response 200 (application/json)

## Providers [/providers?name={name}&country={country}]

OpenBikes uses the data from various providers. Some providers publish data for more than one city.

+ Parameters
    + name - `jcdecaux` (string) The provider you want to filter by.
    + country - `France` (string) The country you want to filter by.

### Retrieve providers [GET]

+ Response 200 (application/json)




## Cities [/cities?name={name}&predictable={predictable}&active={active}&country={country}&provider={provider}]

Each city is located in a country and belongs to a provider. 

+ Parameters
    + name - `Toulouse` (string) The city you want to filter by. 
    + predictable - 0 or 1 (int) 1 if the city allow predictions.
    + active - 0 or 1 (int) 1 if the city is active.
    + country - `France` (string) The country you want to filter by.
    + provider - `jcdecaux` (string) The provider you want to filter by.

### Retrieve cities [GET]

+ Response 200 (application/json)


## Station names [/stations?name={name}&city={city}]

Each city contains stations which each have a name.
+ Parameters
    + name - `00003 - POMME` (optional, string) The bike station which you want to access. Not specifying a city will return all station names.
    + city - `Toulouse` (optional, string) The city which you want to access. Not specifying a city will return the station names for each city.

### Retrieve station names of a city [GET]

+ Response 200 (application/json)


## Countries [/countries/{country}]

Each city is located in one country.

+ Parameters
    + country - `France` (optional, string) The country which you want to access. Not specifying a country will return the cities for each country.

### Retrieve cities of a country [GET]

+ Response 200 (application/json)

        {
            status: "success",
            country: "France",
            cities: [
                "Amiens",
                "Besancon",
                "Cergy-Pontoise",
                "Creteil",
                "Lyon",
                "Marseille",
                "Mulhouse",
                "Nancy",
                "Nantes",
                "Rouen",
                "Toulouse",
                "Rennes",
                "Vannes",
                "Nice",
                "Calais",
                "Montpellier",
                "Avignon",
                "Valence",
                "Strasbourg",
                "Saint-Etienne"
            ]
        }

## Centers [/centers/{city}]

Each city has a geographical center. This is used on the website for centering the map when a user chooses a city. The center's coordinates is the mean of the station coordinates.

+ Parameters
    + city - `Avignon` (optional, string) The city which you want to access. Not specifying a city will return the centers for each city.

### Retrieve city center [GET]

The format for the returned `center` parameter is always [latitude, longitude].

+ Response 200 (application/json)

        {
            status: "success",
            city: "Avignon",
            center: [
                43.9459058,
                4.809686000000001
            ]
        }

## Updates [/updates?city={city}]

City information is meant to be collected every minute or so by the OpenBikes system.

+ Parameters
    + city - `Heidelberg` (optional, string) The city which you want to access. Not specifying a city will return the update times for each city.

### Retrieve the update time for a city [GET]

Timestamps are displayed in seconds.

+ Response 200 (application/json)

        {
            status: "success",
            city: "Heidelberg",
            update: 1457541504
        }

## Predictions [/prediction/city/station/timestamp]

It is possible to make a prediction for the number of bikes and stands that will be available in a station at a certain moment.

+ Parameters
    + city - `Toulouse` (string) The city the station belongs to.
    + station - `00003 - POMME` (string) The name of the station for which the predictions will be made.
    + timestamp - `1457993096` (number) The UNIX timestamp for the prediction.

### Make a prediction for a station at a certain moment [GET]

The returned quantities are best estimates that are updated on a weekly basis. The `std` values represent the standard deviation enabling to compute the confidence intervals of each prediction.

+ Response 200 (application/json)

        {
            status: "success",
            city: "Toulouse",
            station: "00003 - POMME",
            timestamp: 1457993096,
            bikes: {
                "quantity": 1,
                "std": 2.1
            },
            stands: {
                "quantity": 16,
                "std": 1.8
            }
        }