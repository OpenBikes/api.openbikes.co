SELECT AVG(error)
FROM stations, cities, trainings
WHERE stations.city_id = cities.id
AND stations.id = trainings.station_id
AND cities.name = "Toulouse";
