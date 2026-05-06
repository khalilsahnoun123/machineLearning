import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Churn } from './churn';

describe('Churn', () => {
  let component: Churn;
  let fixture: ComponentFixture<Churn>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Churn],
    }).compileComponents();

    fixture = TestBed.createComponent(Churn);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
