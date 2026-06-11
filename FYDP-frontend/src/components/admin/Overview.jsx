import React, { useState, useEffect } from "react";
import axios from "../../utils/axiosInstance";
import {
  Users,
  UserCheck,
  GraduationCap,
  BookOpen,
  Clock,
  User
} from "lucide-react";

const Overview = () => {
  const [stats, setStats] = useState({
    totalAdmins: 0,
    eventAdmins: 0,
    participants: 0,
    students: 0,
    teachers: 0,
    pendingMeetings: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await axios.get("/api/stats/");
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="overview-grid">

      <div className="card">
        <div className="icon blue">
          <Users size={22} />
        </div>
        <div className="card-content">
          <span>Total Admins</span>
          <h2>{loading ? "..." : stats.totalAdmins}</h2>
        </div>
      </div>

      <div className="card">
        <div className="icon purple">
          <UserCheck size={22} />
        </div>
        <div className="card-content">
          <span>Event Admins</span>
          <h2>{loading ? "..." : stats.eventAdmins}</h2>
        </div>
      </div>

      <div className="card">
        <div className="icon green">
          <User size={22} />
        </div>
        <div className="card-content">
          <span>Participants</span>
          <h2>{loading ? "..." : stats.participants}</h2>
        </div>
      </div>

      <div className="card">
        <div className="icon orange">
          <GraduationCap size={22} />
        </div>
        <div className="card-content">
          <span>Students</span>
          <h2>{loading ? "..." : stats.students}</h2>
        </div>
      </div>

      <div className="card">
        <div className="icon cyan">
          <BookOpen size={22} />
        </div>
        <div className="card-content">
          <span>Teachers</span>
          <h2>{loading ? "..." : stats.teachers}</h2>
        </div>
      </div>

      <div className="card">
        <div className="icon red">
          <Clock size={22} />
        </div>
        <div className="card-content">
          <span>Pending Meetings</span>
          <h2>{loading ? "..." : stats.pendingMeetings}</h2>
        </div>
      </div>

    </div>
  );
};

export default Overview;