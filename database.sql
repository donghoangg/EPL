-- 1. Tạo cơ sở dữ liệu
CREATE DATABASE EPL;
USE EPL;

-- 2. Tạo các bảng không có khóa ngoại trước (Bảng cha)

-- Bảng Player
CREATE TABLE Player (
    Player_ID VARCHAR(50) PRIMARY KEY,
    Player_name VARCHAR(255),
    DOB DATE,
    Nation VARCHAR(100),
    Foot VARCHAR(50),
    Position VARCHAR(50),
    Height INT,
    Weight INT
);

-- Bảng Club
CREATE TABLE Club (
    Club_ID VARCHAR(50) PRIMARY KEY,
    Club_Name VARCHAR(255),
    Competition VARCHAR(255)
);

-- Bảng Season
CREATE TABLE Season (
    Season_ID VARCHAR(50) PRIMARY KEY,
    Season VARCHAR(100)
);

-- 3. Tạo các bảng phụ thuộc (Bảng con cấp 1)

-- Bảng Squad_info (Liên kết Club và Season)
CREATE TABLE Squad_info (
    Club_Season_ID VARCHAR(50) PRIMARY KEY,
    Club_ID VARCHAR(50),
    Season_ID VARCHAR(50),
    Num_player INT,
    Age_average DECIMAL(5, 2),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID),
    FOREIGN KEY (Season_ID) REFERENCES Season(Season_ID)
);

-- Bảng Club_player (Liên kết Club và Player)
CREATE TABLE Club_player (
    Club_player_ID VARCHAR(50) PRIMARY KEY,
    Club_ID VARCHAR(50),
    Player_ID VARCHAR(50),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID),
    FOREIGN KEY (Player_ID) REFERENCES Player(Player_ID)
);

-- Bảng Matches (Tên bảng 'Match' thường là từ khóa hệ thống, nên đổi thành Matches hoặc để trong dấu ngoặc)
CREATE TABLE Matches (
    Match_ID VARCHAR(50) PRIMARY KEY,
    Season_ID VARCHAR(50),
    TimePlayed DATE,
    RoundPlayed VARCHAR(50),
    Home_Team VARCHAR(255),
    Away_Team VARCHAR(255),
    Result VARCHAR(50),
    FOREIGN KEY (Season_ID) REFERENCES Season(Season_ID)
);

-- 4. Tạo bảng phụ thuộc cấp 2 (Bảng con của bảng con)

-- Bảng Player_Match_log (Liên kết Club_player và Matches)
CREATE TABLE Player_Match_log (
    Match_Club_player_ID VARCHAR(50) PRIMARY KEY,
    Club_player_ID VARCHAR(50),
    Match_ID VARCHAR(50),
    Start VARCHAR(50),
    Venue VARCHAR(100),
    FOREIGN KEY (Club_player_ID) REFERENCES Club_player(Club_player_ID),
    FOREIGN KEY (Match_ID) REFERENCES Matches(Match_ID)
);

-- player performance 
-- Bang defend
CREATE TABLE Player_Matchlog_Defend (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Num_of_tackle INT,
    Tackle_when_won_poss INT,
    Tackle_in_def INT,
    Tackle_in_mid INT,
    Tackle_in_att INT,
    Dribblers_tackled INT,
    Tackle_challenges INT,
    Per_of_dribblers_tackled DECIMAL(5, 2),
    Tackle_lost INT,
    Num_blocks INT,
    Shot_block INT,
    Pass_block INT,
    Interceptions INT,
    Tackle_and_Interception INT,
    Clearances INT,
    Error INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_defend
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);

-- gca

CREATE TABLE Player_Matchlog_gca (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    SCA INT,
    SCA_per_90 DECIMAL(5, 2),
    SCA_PassLive INT,
    SCA_PassDead INT,
    SCA_TO INT,
    SCA_Shot INT,
    SCA_Fouled INT,
    SCA_Defense INT,
    GCA INT,
    GCA_per_90 DECIMAL(5, 2),
    GCA_PassLive INT,
    GCA_PassDead INT,
    GCA_TO INT,
    GCA_Shot INT,
    GCA_Fouled INT,
    GCA_Defense INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_gca
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);

----- passtype 
CREATE TABLE Player_Matchlog_passtype (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Pass_Attempts INT,
    Pass_Live INT,
    Pass_Dead INT,
    Pass_FK INT,
    Pass_Through_Ball INT,
    Pass_Switch INT,
    Pass_Cross INT,
    Pass_ThrowIn INT,
    Pass_Corner INT,
    Corner_In_Swing INT,
    Corner_Out_Swing INT,
    Corner_Straight INT,
    Pass_Completed INT,
    Pass_Offside INT,
    Pass_Blocked INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_passtype
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);

-- passing 
CREATE TABLE Player_Matchlog_passing (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Pass_Completed_Total INT,
    Pass_Attempted_Total INT,
    Pass_Completion_Per_Total DECIMAL(5, 2),
    Total_Distance INT,
    Progressive_Distance INT,
    Pass_Completed_Short INT,
    Pass_Attempted_Short INT,
    Pass_Completion_Per_Short DECIMAL(5, 2),
    Pass_Completed_Medium INT,
    Pass_Attempted_Medium INT,
    Pass_Completion_Per_Medium DECIMAL(5, 2),
    Pass_Completed_Long INT,
    Pass_Attempted_Long INT,
    Pass_Completion_Per_Long DECIMAL(5, 2),
    Assists INT,
    Expected_Assisted_Goals DECIMAL(5, 2),
    Expected_Assists DECIMAL(5, 2),
    Assist_minus_xAG DECIMAL(5, 2),
    Key_Passes INT,
    Pass_to_Final_Third INT,
    Passes_into_Penalty_Area INT,
    Crosses_into_Penalty_Area INT,
    Progressive_Passes INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_passing
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);

---- possession 
CREATE TABLE Player_Matchlog_possession (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Possession_Percentage DECIMAL(5, 2),
    Total_Touches INT,
    Touches_Defensive_Penalty_Area INT,
    Touches_Defensive_Third INT,
    Touches_Middle_Third INT,
    Touches_Attacking_Third INT,
    Touches_Attacking_Penalty_Area INT,
    Live_Ball_Touches INT,
    Take_On_Attempts INT,
    Take_Ons_Successful INT,
    Take_Ons_Success_Percentage DECIMAL(5, 2),
    Tackled_During_Take_Ons INT,
    Tackled_Percentage DECIMAL(5, 2),
    Total_Carries INT,
    Total_Carrying_Distance INT,
    Progressive_Carrying_Distance INT,
    Progressive_Carries INT,
    Carries_Into_Final_Third INT,
    Carries_Into_Penalty_Area INT,
    Miscontrols INT,
    Dispossessed INT,
    Passes_Received INT,
    Progressive_Passes_Received INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_possession
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);

-- shooting 
CREATE TABLE Player_Matchlog_shooting (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Goals INT,
    Shots INT,
    Shots_On_Target INT,
    Shots_On_Target_Percentage DECIMAL(5, 2),
    Shots_Per_90 DECIMAL(5, 2),
    Shots_On_Target_Per_90 DECIMAL(5, 2),
    Goals_Per_Shot DECIMAL(5, 2),
    Goals_Per_Shot_On_Target DECIMAL(5, 2),
    Average_Shot_Distance DECIMAL(5, 2),
    Free_Kick_Shots INT,
    Penalty_Kicks_Made INT,
    Penalty_Kicks_Attempted INT,
    Expected_Goals DECIMAL(5, 2),
    Non_Penalty_Expected_Goals DECIMAL(5, 2),
    Non_Penalty_xG_Per_Shot DECIMAL(5, 2),
    Goals_Minus_Expected_Goals DECIMAL(5, 2),
    Non_Penalty_Goals_Minus_xG DECIMAL(5, 2),
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_shooting
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);

--standard
CREATE TABLE Player_Matchlog_standard (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Possession_Percentage DECIMAL(5, 2),
    Matches_Played INT,
    Matches_Started INT,
    Minutes_Played INT,
    Ninety_Minutes DECIMAL(5, 2), -- Thường là số phút / 90 (ví dụ 1.0, 0.5) nên để Decimal
    Goals INT,
    Assists INT,
    Goals_And_Assists INT,
    Non_Penalty_Goals INT,
    Penalty_Kicks_Made INT,
    Penalty_Kicks_Attempted INT,
    Yellow_Cards INT,
    Red_Cards INT,
    Expected_Goals DECIMAL(5, 2),
    Non_Penalty_Expected_Goals DECIMAL(5, 2),
    Expected_Assisted_Goals DECIMAL(5, 2),
    Non_Penalty_xG_Plus_xAG DECIMAL(5, 2),
    Progressive_Carries INT,
    Progressive_Passes INT,
    Goals_Per_90 DECIMAL(5, 2),
    Assists_Per_90 DECIMAL(5, 2),
    Goals_And_Assists_Per_90 DECIMAL(5, 2),
    Non_Penalty_Goals_Per_90 DECIMAL(5, 2),
    Goals_And_Assists_Non_Penalty_Per_90 DECIMAL(5, 2),
    Expected_Goals_Per_90 DECIMAL(5, 2),
    Expected_Assisted_Goals_Per_90 DECIMAL(5, 2),
    Expected_Goals_And_Assists_Per_90 DECIMAL(5, 2),
    Non_Penalty_Expected_Goals_Per_90 DECIMAL(5, 2),
    Non_Penalty_xG_Plus_xAG_Per_90 DECIMAL(5, 2),
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_standard
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);
----goalkeeper

CREATE TABLE Player_Matchlog_goalkeeper (
    Match_Club_player_ID VARCHAR(50) NOT NULL,
    Goals_Against INT,
    GA_per_90 DECIMAL(5, 2),
    Shots_on_Target_Against INT,
    Saves INT,
    Save_Percentage DECIMAL(5, 2),
    Wins INT,
    Draws INT,
    Losses INT,
    Clean_Sheets INT,
    Clean_Sheet_Percentage DECIMAL(5, 2),
    PK_Attempted INT,
    PK_Allowed INT,
    PK_Saved INT,
    PK_Missed INT,
    PK_Save_Percentage DECIMAL(5, 2),
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Match_Club_player_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_player_match_log_goalkeeper
    FOREIGN KEY (Match_Club_player_ID) 
    REFERENCES Player_Match_Log(Match_Club_player_ID)
);


-- squad performance
-- Bang defend
CREATE TABLE Squad_Defend (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Num_of_tackle INT,
    Tackle_when_won_poss INT,
    Tackle_in_def INT,
    Tackle_in_mid INT,
    Tackle_in_att INT,
    Dribblers_tackled INT,
    Tackle_challenges INT,
    Per_of_dribblers_tackled DECIMAL(5, 2),
    Tackle_lost INT,
    Num_blocks INT,
    Shot_block INT,
    Pass_block INT,
    Interceptions INT,
    Tackle_and_Interception INT,
    Clearances INT,
    Error INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_defend
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);

-- gca

CREATE TABLE Squad_gca (
    Club_Season_ID VARCHAR(50) NOT NULL,
    SCA INT,
    SCA_per_90 DECIMAL(5, 2),
    SCA_PassLive INT,
    SCA_PassDead INT,
    SCA_TO INT,
    SCA_Shot INT,
    SCA_Fouled INT,
    SCA_Defense INT,
    GCA INT,
    GCA_per_90 DECIMAL(5, 2),
    GCA_PassLive INT,
    GCA_PassDead INT,
    GCA_TO INT,
    GCA_Shot INT,
    GCA_Fouled INT,
    GCA_Defense INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_gca
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);

----- passtype 
CREATE TABLE Squad_passtype (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Pass_Attempts INT,
    Pass_Live INT,
    Pass_Dead INT,
    Pass_FK INT,
    Pass_Through_Ball INT,
    Pass_Switch INT,
    Pass_Cross INT,
    Pass_ThrowIn INT,
    Pass_Corner INT,
    Corner_In_Swing INT,
    Corner_Out_Swing INT,
    Corner_Straight INT,
    Pass_Completed INT,
    Pass_Offside INT,
    Pass_Blocked INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_passtype
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);

-- passing 
CREATE TABLE Squad_passing (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Pass_Completed_Total INT,
    Pass_Attempted_Total INT,
    Pass_Completion_Per_Total DECIMAL(5, 2),
    Total_Distance INT,
    Progressive_Distance INT,
    Pass_Completed_Short INT,
    Pass_Attempted_Short INT,
    Pass_Completion_Per_Short DECIMAL(5, 2),
    Pass_Completed_Medium INT,
    Pass_Attempted_Medium INT,
    Pass_Completion_Per_Medium DECIMAL(5, 2),
    Pass_Completed_Long INT,
    Pass_Attempted_Long INT,
    Pass_Completion_Per_Long DECIMAL(5, 2),
    Assists INT,
    Expected_Assisted_Goals DECIMAL(5, 2),
    Expected_Assists DECIMAL(5, 2),
    Assist_minus_xAG DECIMAL(5, 2),
    Key_Passes INT,
    Pass_to_Final_Third INT,
    Passes_into_Penalty_Area INT,
    Crosses_into_Penalty_Area INT,
    Progressive_Passes INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_passing
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);

---- possession 
CREATE TABLE Squad_possession (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Possession_Percentage DECIMAL(5, 2),
    Total_Touches INT,
    Touches_Defensive_Penalty_Area INT,
    Touches_Defensive_Third INT,
    Touches_Middle_Third INT,
    Touches_Attacking_Third INT,
    Touches_Attacking_Penalty_Area INT,
    Live_Ball_Touches INT,
    Take_On_Attempts INT,
    Take_Ons_Successful INT,
    Take_Ons_Success_Percentage DECIMAL(5, 2),
    Tackled_During_Take_Ons INT,
    Tackled_Percentage DECIMAL(5, 2),
    Total_Carries INT,
    Total_Carrying_Distance INT,
    Progressive_Carrying_Distance INT,
    Progressive_Carries INT,
    Carries_Into_Final_Third INT,
    Carries_Into_Penalty_Area INT,
    Miscontrols INT,
    Dispossessed INT,
    Passes_Received INT,
    Progressive_Passes_Received INT,
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_possession
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);

-- shooting 
CREATE TABLE Squad_shooting (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Goals INT,
    Shots INT,
    Shots_On_Target INT,
    Shots_On_Target_Percentage DECIMAL(5, 2),
    Shots_Per_90 DECIMAL(5, 2),
    Shots_On_Target_Per_90 DECIMAL(5, 2),
    Goals_Per_Shot DECIMAL(5, 2),
    Goals_Per_Shot_On_Target DECIMAL(5, 2),
    Average_Shot_Distance DECIMAL(5, 2),
    Free_Kick_Shots INT,
    Penalty_Kicks_Made INT,
    Penalty_Kicks_Attempted INT,
    Expected_Goals DECIMAL(5, 2),
    Non_Penalty_Expected_Goals DECIMAL(5, 2),
    Non_Penalty_xG_Per_Shot DECIMAL(5, 2),
    Goals_Minus_Expected_Goals DECIMAL(5, 2),
    Non_Penalty_Goals_Minus_xG DECIMAL(5, 2),
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_shooting
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);

--standard
CREATE TABLE Squad_standard (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Possession_Percentage DECIMAL(5, 2),
    Matches_Played INT,
    Matches_Started INT,
    Minutes_Played INT,
    Ninety_Minutes DECIMAL(5, 2), -- Thường là số phút / 90 (ví dụ 1.0, 0.5) nên để Decimal
    Goals INT,
    Assists INT,
    Goals_And_Assists INT,
    Non_Penalty_Goals INT,
    Penalty_Kicks_Made INT,
    Penalty_Kicks_Attempted INT,
    Yellow_Cards INT,
    Red_Cards INT,
    Expected_Goals DECIMAL(5, 2),
    Non_Penalty_Expected_Goals DECIMAL(5, 2),
    Expected_Assisted_Goals DECIMAL(5, 2),
    Non_Penalty_xG_Plus_xAG DECIMAL(5, 2),
    Progressive_Carries INT,
    Progressive_Passes INT,
    Goals_Per_90 DECIMAL(5, 2),
    Assists_Per_90 DECIMAL(5, 2),
    Goals_And_Assists_Per_90 DECIMAL(5, 2),
    Non_Penalty_Goals_Per_90 DECIMAL(5, 2),
    Goals_And_Assists_Non_Penalty_Per_90 DECIMAL(5, 2),
    Expected_Goals_Per_90 DECIMAL(5, 2),
    Expected_Assisted_Goals_Per_90 DECIMAL(5, 2),
    Expected_Goals_And_Assists_Per_90 DECIMAL(5, 2),
    Non_Penalty_Expected_Goals_Per_90 DECIMAL(5, 2),
    Non_Penalty_xG_Plus_xAG_Per_90 DECIMAL(5, 2),
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_standard
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);
----goalkeeper

CREATE TABLE Squad_goalkeeper (
    Club_Season_ID VARCHAR(50) NOT NULL,
    Goals_Against INT,
    GA_per_90 DECIMAL(5, 2),
    Shots_on_Target_Against INT,
    Saves INT,
    Save_Percentage DECIMAL(5, 2),
    Wins INT,
    Draws INT,
    Losses INT,
    Clean_Sheets INT,
    Clean_Sheet_Percentage DECIMAL(5, 2),
    PK_Attempted INT,
    PK_Allowed INT,
    PK_Saved INT,
    PK_Missed INT,
    PK_Save_Percentage DECIMAL(5, 2),
    
    -- Thiết lập khóa chính
    PRIMARY KEY (Club_Season_ID),
    
    -- Thiết lập khóa ngoại liên kết với bảng Player_Match_Log
    CONSTRAINT fk_squad_goalkeeper
    FOREIGN KEY (Club_Season_ID) 
    REFERENCES Squad_info(Club_Season_ID)
);