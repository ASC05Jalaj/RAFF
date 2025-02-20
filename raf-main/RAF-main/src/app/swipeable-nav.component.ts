// swipeable-nav.component.ts
import { Component, OnInit } from '@angular/core';
import { trigger, transition, style, animate, state } from '@angular/animations';

@Component({
  selector: 'app-swipeable-nav',
  template: `
    <div class="nav-container">
      <!-- Navigation Tabs -->
      <div class="flex justify-center bg-white shadow-md mb-6">
        <div 
          *ngFor="let tab of tabs; let i = index" 
          [class]="'px-6 py-3 cursor-pointer transition-all ' + (activeTabIndex === i ? 'border-b-2 border-[#6666CC] text-[#6666CC]' : 'text-gray-600')"
          (click)="setActiveTab(i)"
        >
          {{ tab }}
        </div>
      </div>

      <!-- Content Container -->
      <div 
        class="content-container"
        (touchstart)="onTouchStart($event)"
        (touchmove)="onTouchMove($event)"
        (touchend)="onTouchEnd()"
        [@slideAnimation]="{value: activeTabIndex, params: {slideDirection: slideDirection}}"
      >
        <!-- Summary Section -->
        <div [class.hidden]="activeTabIndex !== 0">
          <ng-content select="[section='summary']"></ng-content>
        </div>

        <!-- HCC Table Section -->
        <!-- <div [class.hidden]="activeTabIndex !== 1">
          <ng-content select="[section='hcc-table']"></ng-content>
        </div> -->

        <!-- Potential Conditions Section -->
        <div [class.hidden]="activeTabIndex !== 1">
          <ng-content select="[section='potential-conditions']"></ng-content>
        </div>
      </div>
    </div>
  `,
  styles: [
    `.nav-container {
      width: 100%;
      overflow: hidden;
    }
    .content-container {
      touch-action: pan-y pinch-zoom;
    }
    .hidden {
      display: none;
    }`
  ],
  animations: [
    trigger('slideAnimation', [
      transition('* => *', [
        style({ transform: '{{slideDirection}}' }),
        animate('300ms ease-out', style({ transform: 'translateX(0)' }))
      ])
    ])
  ]
})
export class SwipeableNavComponent implements OnInit {
  tabs: string[] = ['Summary', 'Potential Conditions'];
  activeTabIndex: number = 0;
  touchStartX: number = 0;
  touchEndX: number = 0;
  slideDirection: string = '';

  ngOnInit() {}

  setActiveTab(index: number) {
    const previousIndex = this.activeTabIndex;
    this.activeTabIndex = index;
    this.slideDirection = previousIndex < index ? 'translateX(-100%)' : 'translateX(100%)';
  }

  onTouchStart(event: TouchEvent) {
    this.touchStartX = event.touches[0].clientX;
  }

  onTouchMove(event: TouchEvent) {
    this.touchEndX = event.touches[0].clientX;
  }

  onTouchEnd() {
    const swipeDistance = this.touchEndX - this.touchStartX;
    const minSwipeDistance = 50;

    if (Math.abs(swipeDistance) > minSwipeDistance) {
      if (swipeDistance > 0 && this.activeTabIndex > 0) {
        // Swipe right
        this.setActiveTab(this.activeTabIndex - 1);
      } else if (swipeDistance < 0 && this.activeTabIndex < this.tabs.length - 1) {
        // Swipe left
        this.setActiveTab(this.activeTabIndex + 1);
      }
    }
  }
}
