import { Component } from '@angular/core';
 
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  exampleData = [
    { diagnosisCode: 'E119', description: 'Diabetes', hccCode: '18', rafScore: '0.182' },
    { diagnosisCode: 'I5020', description: 'Heart Failure', hccCode: '85', rafScore: '0.368' }
  ];
 
}