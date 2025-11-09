import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Import FormsModule
import { TeamService } from '../../services/team.service';
import { Team } from '../../models/team.model';

@Component({
  selector: 'app-team',
  standalone: true,
  imports: [CommonModule, FormsModule], // Add FormsModule here
  templateUrl: './team.component.html',
  styleUrls: ['./team.component.css']
})
export class TeamComponent implements OnInit {
  teams: Team[] = [];
  // Separate models for add and edit forms
  addFormModel: Omit<Team, 'id'> = { name: '' };
  editFormModel: Team = { id: 0, name: '' };
  isEditing = false;

  constructor(private teamService: TeamService) { }

  ngOnInit(): void {
    this.loadTeams();
  }

  loadTeams(): void {
    this.teamService.getTeams().subscribe({
      next: (data) => this.teams = data,
      error: (err) => console.error('Error loading teams:', err)
    });
  }

  addTeam(): void {
    if (!this.addFormModel.name.trim()) return; // Basic validation
    this.teamService.createTeam(this.addFormModel).subscribe({
      next: (team) => {
        this.teams.push(team);
        this.addFormModel = { name: '' }; // Reset add form
      },
      error: (err) => console.error('Error adding team:', err)
    });
  }

  editTeam(team: Team): void {
    this.editFormModel = { ...team }; // Load data into edit form model
    this.isEditing = true;
  }

  updateTeam(): void {
    if (!this.editFormModel.name.trim()) return;
    this.teamService.updateTeam(this.editFormModel.id, { name: this.editFormModel.name }).subscribe({
      next: (updatedTeam) => {
        const index = this.teams.findIndex(t => t.id === updatedTeam.id);
        if (index !== -1) {
          this.teams[index] = updatedTeam;
        }
        this.cancelEdit();
      },
      error: (err) => console.error('Error updating team:', err)
    });
  }

  deleteTeam(id: number): void {
    if (confirm('Are you sure you want to delete this team?')) {
      this.teamService.deleteTeam(id).subscribe({
        next: () => {
          this.teams = this.teams.filter(t => t.id !== id);
          if (this.isEditing && this.editFormModel.id === id) {
            this.cancelEdit(); // Cancel edit if the deleted team was being edited
          }
        },
        error: (err) => console.error('Error deleting team:', err)
      });
    }
  }

  cancelEdit(): void {
    this.editFormModel = { id: 0, name: '' }; // Reset edit form
    this.isEditing = false;
  }
}

