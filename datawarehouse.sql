USE EPL1;

GO 
CREATE VIEW dim_nation AS
SELECT DISTINCT 
    Nation AS nation_id, 
    Nation AS nation
FROM Player
WHERE Nation IS NOT NULL;


select * from dim_nation;

go
CREATE VIEW dim_dominated_foot AS
SELECT DISTINCT 
    Foot AS foot_id, 
    Foot AS foot
FROM Player
WHERE Foot IS NOT NULL;


select * from dim_dominated_foot;

go 
CREATE VIEW Dim_Height AS
SELECT DISTINCT 
    Height AS height_id, 
    Height AS height
FROM Player
WHERE Height IS NOT NULL;


select * from Dim_Height;

go
CREATE VIEW Dim_Weight AS
SELECT DISTINCT 
    Weight AS weight_id, 
    Weight AS weight
FROM Player
WHERE Weight IS NOT NULL;
select * from Dim_Weight ;
go

CREATE VIEW Dim_Club AS
SELECT DISTINCT 
    Club_Name AS club_name_id, 
    Club_Name AS club_name
FROM Club
WHERE Club_Name IS NOT NULL;


select * from Dim_Club;

go
CREATE VIEW Dim_Season AS
SELECT DISTINCT 
    Season AS season_id, 
    Season AS season
FROM Season
WHERE Season IS NOT NULL;

select * from Dim_Season;


GO 
CREATE VIEW Dim_Match AS
SELECT DISTINCT 
    CONCAT(hc.Club_Name, ' vs ', ac.Club_Name) AS match_id,
    CONCAT(hc.Club_Name, ' vs ', ac.Club_Name) AS match_name
FROM Matches m
JOIN Club hc ON m.Home_team = hc.Club_ID
JOIN Club ac ON m.Away_team = ac.Club_ID;



select * from Dim_Match;



GO
CREATE VIEW Dim_Round AS
SELECT DISTINCT 
    Round_played AS round_id, 
    Round_played AS round
FROM Matches
WHERE Round_played IS NOT NULL;
select * from Dim_Round;

go 
CREATE VIEW Dim_Result AS
SELECT DISTINCT 
    Result AS result_id, 
    Result AS result
FROM Matches
WHERE Result IS NOT NULL;

select * from Dim_Result;
GO
CREATE VIEW Dim_Start AS
SELECT DISTINCT 
    Start AS start_id, 
    Start AS start
FROM Player_Match_log
WHERE Start IS NOT NULL;

select * from Dim_Start;
GO
CREATE VIEW Dim_Venue AS
SELECT DISTINCT 
    Venue AS venue_id, 
    Venue AS venue
FROM Player_Match_log
WHERE Venue IS NOT NULL;

Select * from Dim_Venue;

GO
CREATE VIEW Dim_position AS
SELECT DISTINCT 
    Pos AS position_id, 
    Pos AS position
FROM Player_Match_log
WHERE Pos IS NOT NULL;
select * from Dim_position;


select * from Fact_Player_performance

GO
CREATE VIEW Fact_Player_performance AS
SELECT 
    -- Lấy ID duy nhất từ tất cả các bảng bằng COALESCE
    COALESCE(s.Club_player_matchlog_ID, d.Club_player_matchlog_ID, g.Club_player_matchlog_ID, 
             pt.Club_player_matchlog_ID, p.Club_player_matchlog_ID, pos.Club_player_matchlog_ID) AS Club_player_matchlog_ID,

    -- 1. Chỉ số từ bảng Player_Matchlog_standard
    s.Goals, s.Assists, s.Penalty_kicks_made, s.Penalty_kicks_attempted, s.Shot_total, s.Shot_on_target, 
    s.Yellow_Cards, s.Red_Cards, s.Touches, s.Tackles, s.Interceptions, s.Blocks, s.Expected_Goals, 
    s.Non_Penalty_Expected_Goals, s.Expected_Assisted_Goals, s.Shot_creation, s.Goal_creation, 
    s.Pass_complete, s.Pass_attemp, s.Pass_completion, s.Progressive_Passes, s.Carries, 
    s.Progressive_Carries, s.Take_on_attemp, s.Take_on_successful,

    -- 2. Chỉ số từ bảng Player_Matchlog_Defend
    d.Num_of_tackle, d.Tackle_when_won_poss, d.Tackle_in_def, d.Tackle_in_mid, d.Tackle_in_att, 
    d.Dribblers_tackled, d.Tackle_challenges, d.Per_of_dribblers_tackled, d.Tackle_lost, 
    d.Num_blocks, d.Shot_block, d.Pass_block, d.Interceptions AS Interceptions_Def, -- Trùng tên
    d.Tackle_and_Interception, d.Clearances, d.Error,

    -- 3. Chỉ số từ bảng Player_Matchlog_gca
    g.SCA, g.SCA_PassLive, g.SCA_PassDead, g.SCA_TO, g.SCA_Shot, g.SCA_Fouled, g.SCA_Defense, 
    g.GCA, g.GCA_PassLive, g.GCA_PassDead, g.GCA_TO, g.GCA_Shot, g.GCA_Fouled, g.GCA_Defense,

    -- 4. Chỉ số từ bảng Player_Matchlog_passtype
    pt.Pass_Attempts, pt.Pass_Live, pt.Pass_Dead, pt.Pass_FK, pt.Pass_Through_Ball, 
    pt.Pass_Switch, pt.Pass_Cross, pt.Pass_ThrowIn, pt.Pass_Corner, pt.Corner_In_Swing, 
    pt.Corner_Out_Swing, pt.Corner_Straight, pt.Pass_Completed, pt.Pass_Offside, pt.Pass_Blocked,

    -- 5. Chỉ số từ bảng Player_Matchlog_passing
    p.Pass_Completed_Total, p.Pass_Attempted_Total, p.Pass_Completion_Per_Total, p.Total_Distance, 
    p.Progressive_Distance, p.Pass_Completed_Short, p.Pass_Attempted_Short, p.Pass_Completion_Per_Short, 
    p.Pass_Completed_Medium, p.Pass_Attempted_Medium, p.Pass_Completion_Per_Medium, p.Pass_Completed_Long, 
    p.Pass_Attempted_Long, p.Pass_Completion_Per_Long, p.Assists AS Assists_Passing, -- Trùng tên
    p.Expected_Assisted_Goals AS xAG_Passing, -- Trùng tên
    p.Expected_Assists, p.Key_Passes, p.Pass_to_Final_Third, p.Passes_into_Penalty_Area, 
    p.Crosses_into_Penalty_Area, p.Progressive_Passes AS Progressive_Passes_Passing, -- Trùng tên

    -- 6. Chỉ số từ bảng Player_Matchlog_possession
    pos.Total_Touches, pos.Touches_Defensive_Penalty_Area, pos.Touches_Defensive_Third, 
    pos.Touches_Middle_Third, pos.Touches_Attacking_Third, pos.Touches_Attacking_Penalty_Area, 
    pos.Live_Ball_Touches, pos.Take_On_Attempts, pos.Take_Ons_Successful, pos.Take_Ons_Success_Percentage, 
    pos.Tackled_During_Take_Ons, pos.Tackled_Percentage, pos.Total_Carries, pos.Total_Carrying_Distance, 
    pos.Progressive_Carrying_Distance, pos.Progressive_Carries AS Progressive_Carries_Pos, -- Trùng tên
    pos.Carries_Into_Final_Third, pos.Carries_Into_Penalty_Area, pos.Miscontrols, pos.Dispossessed, 
    pos.Passes_Received, pos.Progressive_Passes_Received

FROM Player_Matchlog_standard s
FULL OUTER JOIN Player_Matchlog_Defend d ON s.Club_player_matchlog_ID = d.Club_player_matchlog_ID
FULL OUTER JOIN Player_Matchlog_gca g ON COALESCE(s.Club_player_matchlog_ID, d.Club_player_matchlog_ID) = g.Club_player_matchlog_ID
FULL OUTER JOIN Player_Matchlog_passtype pt ON COALESCE(s.Club_player_matchlog_ID, d.Club_player_matchlog_ID, g.Club_player_matchlog_ID) = pt.Club_player_matchlog_ID
FULL OUTER JOIN Player_Matchlog_passing p ON COALESCE(s.Club_player_matchlog_ID, d.Club_player_matchlog_ID, g.Club_player_matchlog_ID, pt.Club_player_matchlog_ID) = p.Club_player_matchlog_ID
FULL OUTER JOIN Player_Matchlog_possession pos ON COALESCE(s.Club_player_matchlog_ID, d.Club_player_matchlog_ID, g.Club_player_matchlog_ID, pt.Club_player_matchlog_ID, p.Club_player_matchlog_ID) = pos.Club_player_matchlog_ID;


GO
CREATE VIEW Fact_Goalkeeper_performance AS
SELECT 
    Club_player_matchlog_ID,
    
    -- Chỉ số cản phá cơ bản
    Shots_on_Target_Against,
    Goals_Against,
    Saves,
    Save_Percentage,
    Clean_Sheets,
    
    -- Chỉ số Penalty
    PK_Attempted,
    PK_Allowed,
    PK_Saved,
    PK_Missed,
    
    -- Chỉ số nâng cao (đã thêm qua ALTER TABLE)
    Post_Shot_xG,
    Pass_Completed,
    Pass_Attempted,
    Pass_Percentage,
    Pass_Attempted_GK,
    Throws_Attempted,
    Launch_Percentage,
    Avg_Pass_Length,
    Goal_Kicks_Attempted,
    Goal_Kick_Launch_Percentage,
    Avg_Goal_Kick_Length,
    
    -- Chỉ số phòng ngự chủ động
    Crosses_Faced,
    Crosses_Stopped,
    Cross_Stop_Percentage,
    Def_Actions_Outside_PA,
    Avg_Distance_Def_Actions

FROM Player_Matchlog_goalkeeper;



CREATE TABLE dim_date (
    idDate DATE PRIMARY KEY,
    day INT,
    month INT,
    quarter INT,
    year INT
);
GO 
CREATE PROCEDURE dbo.FillDates (@dateStart DATE, @dateEnd DATE)
AS
BEGIN
    WHILE @dateStart <= @dateEnd
    BEGIN
        INSERT INTO dim_date (idDate, day, month, quarter, year)
        VALUES (@dateStart, DAY(@dateStart), MONTH(@dateStart), DATEPART(QUARTER, @dateStart), YEAR(@dateStart));
        
        SET @dateStart = DATEADD(DAY, 1, @dateStart);
    END
END;

EXEC dbo.FillDates '2018-01-01', '2026-12-31';

select * from dim_date;