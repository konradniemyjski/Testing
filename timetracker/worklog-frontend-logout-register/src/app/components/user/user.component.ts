import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { TeamService } from '../../services/team.service'; // Import TeamService
import { User } from '../../models/user.model';
import { Team } from '../../models/team.model'; // Import Team model

@Component({
  selector: 'app-user',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent implements OnInit {
  users: User[] = [];
  teams: Team[] = []; // To populate the team dropdown
  // Separate models for add and edit forms
  addFormModel: Omit<User, 'id' | 'teamName'> = { name: '', surname: '', teamId: 0 };
  editFormModel: User = { id: 0, name: '', surname: '', teamId: 0, teamName: '' };
  isEditing = false;

  constructor(
    private userService: UserService,
    private teamService: TeamService // Inject TeamService
  ) { }

  ngOnInit(): void {
    this.loadUsers();
    this.loadTeams(); // Load teams for the dropdown
  }

  loadUsers(): void {
    this.userService.getUsers().subscribe({
      next: (data) => this.users = data,
      error: (err) => console.error('Error loading users:', err)
    });
  }

  loadTeams(): void {
    this.teamService.getTeams().subscribe({
      next: (data) => this.teams = data,
      error: (err) => console.error('Error loading teams:', err)
    });
  }

  addUser(): void {
    if (!this.addFormModel.name.trim() || !this.addFormModel.surname.trim() || !this.addFormModel.teamId) return;
    this.userService.createUser(this.addFormModel).subscribe({
      next: (user) => {
        this.loadUsers(); // Simple reload for now
        this.addFormModel = { name: '', surname: '', teamId: 0 }; // Reset add form
      },
      error: (err) => console.error('Error adding user:', err)
    });
  }

  editUser(user: User): void {
    this.editFormModel = { ...user }; // Load data into edit form model
    this.isEditing = true;
  }

  updateUser(): void {
    if (!this.editFormModel.name.trim() || !this.editFormModel.surname.trim() || !this.editFormModel.teamId) return;
    const userToUpdate: Omit<User, 'id' | 'teamName'> = {
        name: this.editFormModel.name,
        surname: this.editFormModel.surname,
        teamId: this.editFormModel.teamId
    };
    this.userService.updateUser(this.editFormModel.id, userToUpdate).subscribe({
      next: (updatedUser) => {
        this.loadUsers(); // Reload users to reflect changes
        this.cancelEdit();
      },
      error: (err) => console.error('Error updating user:', err)
    });
  }

  deleteUser(id: number): void {
    if (confirm('Are you sure you want to delete this user?')) {
      this.userService.deleteUser(id).subscribe({
        next: () => {
          this.users = this.users.filter(u => u.id !== id);
          if (this.isEditing && this.editFormModel.id === id) {
            this.cancelEdit(); // Cancel edit if the deleted user was being edited
          }
        },
        error: (err) => console.error('Error deleting user:', err)
      });
    }
  }

  cancelEdit(): void {
    this.editFormModel = { id: 0, name: '', surname: '', teamId: 0, teamName: '' }; // Reset edit form
    this.isEditing = false;
  }
}

