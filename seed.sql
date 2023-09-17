\c optimal

-- INSERT INTO ratings(mood, took_all_meds, ef_rating, med_rating, notes, date, user_id)
-- VALUES(4, True, 7, 2, '', '2023-09-08', 2),
--      (6, True, 4, 8, '', '2023-09-07', 2),
--      (7, False, 3, 5, '', '2023-09-10', 2),
--      (7, False, 3, 5, '', '2023-09-01', 2),
--      (4, True, 4, 6, '', '2023-09-06', 2),
--      (9, True, 9, 6, '', '2023-09-05', 2),
--      (5, True, 4, 8, '', '2023-09-07', 1),
--      (9, False, 5, 4, '', '2023-09-08', 1);

INSERT INTO factors(name)
VALUES('Social Interactions'),
      ('Level of Exercise'),
      ('My Work Day'),        
      ('My Day at School'),
      ('Diet'),
      ('Level of Stress'),
      ('Personal Health'),
      ('My Productivity'), 
      ('Sleep Quality');  
            


\q