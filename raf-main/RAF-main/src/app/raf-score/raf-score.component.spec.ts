import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RafScoreComponent } from './raf-score.component';

describe('RafScoreComponent', () => {
  let component: RafScoreComponent;
  let fixture: ComponentFixture<RafScoreComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RafScoreComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RafScoreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
