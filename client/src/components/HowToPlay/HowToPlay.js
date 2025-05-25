import React from 'react';

const HowToPlay = () => {
  const steps = [
    {
      number: 1,
      title: "Generate Your Board and Study Your Targets",
      description: "Start your hunting journey by generating your personalized bingo board. Take some time to carefully review each character slot and familiarize yourself with their unique designs, outfits, and distinctive features. If you encounter characters you don't recognize, don't worry! Click on the details section for each character to learn more about their series, personality, and key visual elements. This preparation phase is crucial for successful hunting at the convention.",
      image: "1 - Generate your board and some time to review it. Familiarize yourself with the characters If you don't recognize them, check out the details section for more.png",
      position: "left"
    },
    {
      number: 2,
      title: "Explore the Convention and Scout for Cosplayers",
      description: "Armed with your knowledge, venture into the convention halls or attend dedicated cosplay meetups and photoshoot gatherings. Keep your eyes peeled as you navigate through crowds, artist alleys, and popular photo spots. When you spot a character from your board, that's your moment to shine! Remember that conventions are bustling environments, so stay alert and patient – your target cosplayers might appear when you least expect them.",
      image: "2 - Explore the convention or attend cosplay meetups. If you spot a character from your board then you're in luck!.png",
      position: "right"
    },
    {
      number: 3,
      title: "Approach with Respect and Ask for Permission",
      description: "Even if you're feeling shy or nervous, remember to approach cosplayers with confidence and respect. Cosplayers invest countless hours crafting their costumes and embodying their characters – one of the most rewarding feelings for them is being recognized and appreciated for their hard work. However, always remember that cosplay is NOT consent. Politely introduce yourself, compliment their craftsmanship, and ask for permission before taking any photos. Most cosplayers are happy to pose when approached respectfully!",
      image: "3 - Even if your feeling shy, approach them and ask for a picture. Cosplayers work hard on their costumes and one of the most rewarding feelings is to be recognized and appreciated. That being said, cosplay is not consent, always ask for permission.png",
      position: "left"
    },
    {
      number: 4,
      title: "Capture the Perfect Photo Together",
      description: "Once you have permission, it's time to get that winning shot! Make sure you're featured in the photo in some way – whether it's a full pose together, a selfie-style shot, or even just your hand giving a thumbs up in the corner of the frame. The key requirement is that you must be visible in the photo to claim the square. Unless it's your preference, don't worry about getting the perfect shot!",
      image: "4 - Get a photo of yourself with the cosplay. You must be featured in the photo in some way even if it's just your hand giving a thumbs up..png",
      position: "right"
    },
    {
      number: 5,
      title: "Upload and Claim Your Victory",
      description: "The final step in your hunting process! Upload your photos to your team's bingo board to officially claim each slot and start accumulating those valuable points. Each successful claim brings you closer to filling your board and achieving the ultimate goal – becoming a licensed Bimbo Hunter! Keep track of your progress and celebrate each victory as you work towards completing your board and earning your place on the leaderboard.",
      image: "5 - Upload your photos to your team's bingo board to claim the slot. Fill your slots to earn points and become a licensed Bimbo Hunter!.png",
      position: "left"
    }
  ];

  return (
    <div className="how-to-play-container">
      <div className="how-to-play-header">
        <h1>How to Become a Licensed Bimbo Hunter</h1>
        <p className="wikihow-subtitle">A Complete Guide to Mastering the Art of Cosplay Hunting</p>
        <div className="wikihow-meta">
          <span className="difficulty">Difficulty: Beginner</span>
          <span className="time">Time Required: Convention Duration</span>
          <span className="steps">5 Steps</span>
        </div>
      </div>

      <div className="how-to-play-content">
        <div className="wikihow-intro">
          <p>
            Welcome to the ultimate guide for becoming a certified Bimbo Hunter! This comprehensive tutorial will walk you through
            the essential steps needed to master the art of cosplay hunting at conventions. Whether you're a shy beginner or an
            experienced convention-goer, this guide will help you navigate the exciting world of cosplay photography and bingo board completion.
          </p>
        </div>

        <div className="wikihow-steps">
          {steps.map((step, index) => (
            <div key={index} className={`wikihow-step ${step.position}`}>
              <div className="step-content">
                <div className="step-header">
                  <span className="step-number">{step.number}</span>
                  <h2 className="step-title">{step.title}</h2>
                </div>
                <div className="step-body">
                  <div className="step-text">
                    <p>{step.description}</p>
                  </div>
                  <div className="step-image">
                    <img
                      src={`${process.env.PUBLIC_URL}/How To/${step.image}`}
                      alt={`Step ${step.number}: ${step.title}`}
                      className="wikihow-image"
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="wikihow-conclusion">
          <h3>Congratulations!</h3>
          <p>
            You now have all the knowledge needed to become a successful Bimbo Hunter! Remember to always be respectful,
            have fun, and celebrate the amazing creativity of the cosplay community. Good luck on your hunting adventure!
          </p>
        </div>
      </div>
    </div>
  );
};

export default HowToPlay;
