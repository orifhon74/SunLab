drop table Users;
drop table AccessRecords;

create table Users (
	userID varchar(15) primary key,
    user_name varchar(20),
    user_type varchar(10),
    user_status boolean
);

create table AccessRecords (
    userID varchar(15),
    user_name varchar(20),
    timestamp TIMESTAMP,
    entryType varchar(5),
    foreign key (userID) references Users(userID)
);

insert into Users values ('971206576', 'Orifkhon Kilichev', 'Student', True);
insert into Users values ('070120038', 'Muxsina Usmonova', 'Student', True);
insert into Users values ('091234523', 'Celeste Curtis', 'Student', True);
insert into Users values ('987654316', 'Mathew Benton', 'Faculty', True);
insert into Users values ('010375490', 'Josh Clay', 'Staff', True);
insert into Users values ('757567267', 'Nigel Gaines', 'Student', True);
insert into Users values ('223445945', 'Linwood Carlson', 'Student', True);
insert into Users values ('306873221', 'Theo Reese', 'Faculty', True);
insert into Users values ('320596783', 'Lillie Wise', 'Student', True);
insert into Users values ('674757722', 'Wanda James', 'Janitor', True);
insert into Users values ('127890011', 'Cameron Larson', 'Admin', True);


