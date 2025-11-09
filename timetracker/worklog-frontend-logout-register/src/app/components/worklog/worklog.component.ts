import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { WorklogService } from '../../services/worklog.service';
import { UserService } from '../../services/user.service'; // Import UserService
import { Worklog } from '../../models/worklog.model';
import { User } from '../../models/user.model'; // Import User model

@Component({
  selector: 'app-worklog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './worklog.component.html',
  styleUrls: ['./worklog.component.css']
})
export class WorklogComponent implements OnInit {
  worklogs: Worklog[] = [];
  users: User[] = []; // To populate the user dropdown

  // Separate models for add and edit forms
  addFormModel: Omit<Worklog, 'id' | 'userName' | 'userSurname'> = {
    workDate: new Date().toISOString().split('T')[0], // Default to today
    userId: 0,
    timeSpent: 0,
    mealsOrdered: 0,
    nightsSpent: 0
  };
  editFormModel: Worklog = {
    id: 0,
    workDate: '',
    userId: 0,
    timeSpent: 0,
    mealsOrdered: 0,
    nightsSpent: 0
  };
  isEditing = false;

  constructor(
    private worklogService: WorklogService,
    private userService: UserService // Inject UserService
  ) { }

  ngOnInit(): void {
    this.loadWorklogs();
    this.loadUsers(); // Load users for the dropdown
  }

  loadWorklogs(): void {
    this.worklogService.getWorklogs().subscribe({
      next: (data) => this.worklogs = data,
      error: (err) => console.error('Error loading worklogs:', err)
    });
  }

  loadUsers(): void {
    this.userService.getUsers().subscribe({
      next: (data) => this.users = data,
      error: (err) => console.error('Error loading users:', err)
    });
  }

  addWorklog(): void {
    if (!this.addFormModel.workDate || !this.addFormModel.userId || this.addFormModel.timeSpent <= 0) return; // Basic validation
    this.worklogService.createWorklog(this.addFormModel).subscribe({
      next: (worklog) => {
        this.loadWorklogs(); // Reload worklogs
        this.resetAddForm();
      },
      error: (err) => console.error('Error adding worklog:', err)
    });
  }

  editWorklog(worklog: Worklog): void {
    this.editFormModel = { ...worklog };
    // Ensure date is in 'yyyy-MM-dd' format for the input type="date"
    this.editFormModel.workDate = new Date(worklog.workDate).toISOString().split('T')[0];
    this.isEditing = true;
  }

  updateWorklog(): void {
    if (!this.editFormModel.workDate || !this.editFormModel.userId || this.editFormModel.timeSpent <= 0) return;
    const worklogToUpdate: Omit<Worklog, 'id' | 'userName' | 'userSurname'> = {
        workDate: this.editFormModel.workDate,
        userId: this.editFormModel.userId,
        timeSpent: this.editFormModel.timeSpent,
        mealsOrdered: this.editFormModel.mealsOrdered,
        nightsSpent: this.editFormModel.nightsSpent
    };
    this.worklogService.updateWorklog(this.editFormModel.id, worklogToUpdate).subscribe({
      next: (updatedWorklog) => {
        this.loadWorklogs(); // Reload worklogs
        this.cancelEdit();
      },
      error: (err) => console.error('Error updating worklog:', err)
    });
  }

  deleteWorklog(id: number): void {
    if (confirm('Are you sure you want to delete this worklog entry?')) {
      this.worklogService.deleteWorklog(id).subscribe({
        next: () => {
          this.worklogs = this.worklogs.filter(w => w.id !== id);
           if (this.isEditing && this.editFormModel.id === id) {
            this.cancelEdit(); // Cancel edit if the deleted worklog was being edited
          }
        },
        error: (err) => console.error('Error deleting worklog:', err)
      });
    }
  }

  cancelEdit(): void {
    this.resetEditForm();
    this.isEditing = false;
  }

  resetAddForm(): void {
     this.addFormModel = {
        workDate: new Date().toISOString().split('T')[0],
        userId: 0,
        timeSpent: 0,
        mealsOrdered: 0,
        nightsSpent: 0
      };
  }

  resetEditForm(): void {
     this.editFormModel = {
        id: 0,
        workDate: '',
        userId: 0,
        timeSpent: 0,
        mealsOrdered: 0,
        nightsSpent: 0
      };
  }

  // Implement XLS download trigger (Step 7.2)
  downloadXls(): void {
    this.worklogService.downloadWorklogsXls().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'worklogs.xlsx'; // Set the file name
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      },
      error: (err) => console.error('Error downloading XLS:', err)
    });
  }
}

