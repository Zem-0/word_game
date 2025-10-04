INSERT INTO word (word) VALUES 
('APPLE'),
('BRAVE'),
('CHESS'),
('DRIVE'),
('EAGLE'),
('FAITH'),
('GRAPE'),
('HOUSE'),
('INPUT'),
('JUMBO')
ON CONFLICT (word) DO NOTHING;