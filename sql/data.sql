PRAGMA foreign_keys = ON;

INSERT INTO users (username, fullname, email, filename, password, created)
VALUES
  ('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', CURRENT_TIMESTAMP),
  ('jflinn', 'Jason Flinn', 'jflinn@umich.edu', '505083b8b56c97429a728b68f31b0b2a089e5113.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', CURRENT_TIMESTAMP),
  ('michjc', 'Michael Cafarella', 'michjc@umich.edu', '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', CURRENT_TIMESTAMP),
  ('jag', 'H.V. Jagadish', 'jag@umich.edu', '73ab33bd357c3fd42292487b825880958c595655.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', CURRENT_TIMESTAMP);

INSERT INTO posts (postid, filename, owner, created)
VALUES
  (1, '122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 'awdeorio', CURRENT_TIMESTAMP),
  (2, 'ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 'jflinn', CURRENT_TIMESTAMP),
  (3, '9887e06812ef434d291e4936417d125cd594b38a.jpg', 'awdeorio', CURRENT_TIMESTAMP),
  (4, '2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 'jag', CURRENT_TIMESTAMP);

INSERT INTO following (username1, username2, created)
VALUES
  ('awdeorio', 'jflinn', CURRENT_TIMESTAMP),
  ('awdeorio', 'michjc', CURRENT_TIMESTAMP),
  ('jflinn', 'awdeorio', CURRENT_TIMESTAMP),
  ('jflinn', 'michjc', CURRENT_TIMESTAMP),
  ('michjc', 'awdeorio', CURRENT_TIMESTAMP),
  ('michjc', 'jag', CURRENT_TIMESTAMP),
  ('jag', 'michjc', CURRENT_TIMESTAMP);

INSERT INTO comments (commentid, owner, postid, text, created)
VALUES
  (1, 'awdeorio', 3, '#chickensofinstagram', '2017-06-20 15:47:02'),
  (2, 'jflinn', 3, 'I <3 chickens', '2017-06-20 15:47:02'),
  (3, 'michjc', 3, 'Cute overload!', '2017-06-20 15:47:02'),
  (4, 'awdeorio', 2, 'Sick #crossword', '2017-06-20 15:47:02'),
  (5, 'jflinn', 1, 'Walking the plank #chickensofinstagram', '2017-06-20 15:47:02'),
  (6, 'awdeorio', 1, 'This was after trying to teach them to do a #crossword', '2017-06-20 15:47:02'),
  (7, 'jag', 4, 'Saw this on the diag yesterday!', '2017-06-20 15:47:02');

INSERT INTO likes (likeid, owner, postid, created)
VALUES
  (1, 'awdeorio', 1, '2017-06-20 15:47:02'),
  (2, 'michjc', 1, '2017-06-20 15:47:02'),
  (3, 'jflinn', 1, '2017-06-20 15:47:02'),
  (4, 'awdeorio', 2, '2017-06-20 15:47:02'),
  (5, 'michjc', 2, '2017-06-20 15:47:02'),
  (6, 'awdeorio', 3, '2017-06-20 15:47:02');